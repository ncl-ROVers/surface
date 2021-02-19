"""
Data segment module for lower-level operations with Redis.
"""
from typing import Iterable
import msgpack
from msgpack import UnpackException, PackException
from redis import Redis, RedisError
from ..utils import logger
from ..exceptions import DataManagerException


class DataSegment:
    """
    Handle storing and updating values related to a specific set of keys.

    Upon initialisation, a new collection of keys is stored in Redis. Any attempts to get or set the data once its
    created will verify that a subset of this collection is used. Graceful error handling or error raising will be used
    depending on the context.

    Each data segment should be registered within the data manager, and can be used as follows:

        print(segment["some-key"])  # Get value
        segment["some-key"] = 10  # Set value
        print(segment.all)  # Get all (key, value) pairs as a dictionary
        segment.fetch({"some-key", "some-other-key"})  # Get multiple (key, value) pairs as a dictionary
        segment.update({"some-key": 10, "some-other-key": 20})  # Set multiple (key, value) pairs using a dictionary

    The `DataManagerException` error will be thrown in most cases - see details for each function.
    """

    def __init__(self, name: str, cache: Redis, data: dict):
        """
        Create a new data segment.

        Name will be used to guarantee uniqueness of keys within each segment, rather than across the entire cache. This
        means that key collisions between two different data segments are allowed.

        Data will be used to initialise the cache with defaults, as well as store the keys for future reference.
        """
        self._keys = tuple(data.keys())
        self._cache = cache
        self._name = name

        try:
            for key, value in data.items():
                redis_key = self._build_redis_key(key)
                if self._cache.exists(redis_key):
                    logger.debug(f"Key {key} already existed at the initialisation of data segment {self._name}, "
                                 f"and will get overridden")
                self._cache.set(redis_key, msgpack.packb(value))
        except (RedisError, PackException) as ex:
            raise DataManagerException(f"Failed to initialise the data segment {self._name}") from ex

    def __getitem__(self, key, unpack: bool = True):
        """
        Retrieve an item from the cache.

        Optionally (and by default) convert the item from bytes to the relevant Python object.

        `DataManagerException` will be thrown if the key wasn't registered at `__init__`, or in case of Redis and bytes
        conversion errors.
        """
        if key not in self._keys:
            raise DataManagerException(f"Failed to retrieve value using key {key} - key not registered")

        redis_key = self._build_redis_key(key)
        try:
            value = self._cache.get(redis_key)
            return msgpack.unpackb(value) if unpack else value
        except (RedisError, UnpackException) as ex:
            raise DataManagerException(f"Failed to retrieve value using key {key}") from ex

    def __setitem__(self, key, value):
        """
        Retrieve an item from the cache.

        `DataManagerException` will be thrown if the key wasn't registered at `__init__`, or in case of Redis and bytes
        conversion errors.
        """
        if key not in self._keys:
            raise DataManagerException(f"Failed to set value using key {key} - key not registered")

        redis_key = self._build_redis_key(key)
        try:
            redis_value = value if isinstance(value, bytes) else msgpack.packb(value)
            self._cache.set(redis_key, redis_value)
        except (RedisError, PackException) as ex:
            raise DataManagerException(f"Failed to save value {value} using key {key}") from ex

    def all(self, unpack: bool = True) -> dict:
        """
        Retrieve all stored (key, value) pairs.

        Optionally (and by default) convert all items from bytes to the relevant Python object.

        `DataManagerException` will be thrown in case of `__getitem__` errors.
        """
        return {key: self.__getitem__(key, unpack) for key in self._keys}

    def fetch(self, keys: Iterable, unpack: bool = True):
        """
        Retrieve a subset of all stored (key, value) pairs.

        Optionally (and by default) convert all items from bytes to the relevant Python object.

        `DataManagerException` will be thrown in case of `__getitem__` errors. Non-registered keys will be ignored.
        """
        data = dict()

        for key in keys:
            redis_key = self._build_redis_key(key)
            if not self._cache.exists(redis_key):
                logger.warning(f"Skipping fetching key {key} for data segment {self._name} - key not registered")
                continue
            data[key] = self.__getitem__(key, unpack)

        return data

    def update(self, data: dict):
        """
        Retrieve a subset of all stored (key, value) pairs.

        `DataManagerException` will be thrown in case of `__setitem__` errors. Non-registered keys will be ignored.
        """
        for key, value in data.items():
            redis_key = self._build_redis_key(key)
            if not self._cache.exists(redis_key):
                logger.warning(f"Skipping updating key {key} for data segment {self._name} - key not registered")
                continue
            self.__setitem__(key, value)

    def _build_redis_key(self, key: str) -> str:
        """
        Build a redis key string that guarantees uniqueness with respect to this data segment.
        """
        return self._name + ":" + key
