"""
Data manager module for dispatching information to different components of the vehicle.
"""
from typing import Iterable
from redis import Redis, RedisError
from .utils import logger, classproperty
from .constants import REDIS_HOST, REDIS_PORT
from .exceptions import DataManagerException


class _DataSegment:
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
            for key, value in data:
                redis_key = self._build_redis_key(key)
                if self._cache.exists(redis_key):
                    logger.warning(f"Key {key} already existed at the initialisation of data segment {self._name}, "
                                   f"and will get overridden")
                self._cache.set(redis_key, bytes(value))
        except RedisError as ex:
            raise DataManagerException(f"Failed to initialise the data segment {self._name}") from ex

    def __getitem__(self, key):
        """
        Retrieve an item from the cache.

        `DataManagerException` will be thrown if the key wasn't registered at `__init__`, or in case of Redis errors.
        """
        if key not in self._keys:
            raise DataManagerException(f"Failed to retrieve value using key {key} - key not registered")

        redis_key = self._build_redis_key(key)
        try:
            return self._cache.get(redis_key)
        except RedisError as ex:
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
            self._cache.set(redis_key, bytes(value))
        except (RedisError, TypeError) as ex:
            raise DataManagerException(f"Failed to save value {value} using key {key}") from ex

    @property
    def all(self) -> dict:
        """
        Retrieve all stored (key, value) pairs.

        `DataManagerException` will be thrown in case of Redis errors.
        """
        data = dict()

        for key in self._keys:
            try:
                redis_key = self._build_redis_key(key)
                data[key] = self._cache.get(redis_key)
            except RedisError as ex:
                raise DataManagerException(f"Failed to retrieve value using key {key}") from ex

        return data

    def fetch(self, keys: Iterable):
        """
        Retrieve a subset of all stored (key, value) pairs.

        `DataManagerException` will be thrown in case of Redis errors. Non-registered keys will be ignored.
        """
        data = dict()

        try:
            for key in keys:
                redis_key = self._build_redis_key(key)
                if not self._cache.exists(redis_key):
                    logger.warning(f"Skipping fetching key {key} for data segment {self._name} - key not registered")
                    continue
                data[key] = self._cache.get(redis_key)
        except RedisError as ex:
            raise DataManagerException(f"Failed to fetch the data segment {self._name} using keys {keys}") from ex

        return data

    def update(self, data: dict):
        """
        Retrieve a subset of all stored (key, value) pairs.

        `DataManagerException` will be thrown in case of Redis or bytes conversion errors. Non-registered keys will
        be ignored.
        """
        try:
            for key, value in data:
                redis_key = self._build_redis_key(key)
                if not self._cache.exists(redis_key):
                    logger.warning(f"Skipping updating key {key} for data segment {self._name} - key not registered")
                    continue
                self._cache.set(redis_key, bytes(value))
        except (RedisError, TypeError) as ex:
            raise DataManagerException(f"Failed to update the data segment {self._name} using data {data}") from ex

    def _build_redis_key(self, key: str) -> str:
        """
        Build a redis key string that guarantees uniqueness with respect to this data segment.
        """
        return self._name + "-" + key


# noinspection PyMethodParameters
class DataManager:
    """
    Handle creation of each data segment and access to it.

    Currently the segments are as follows:

        - TODO
        - TODO
        - TODO

    Keep in mind that each segment MUST have a unique name to avoid key collisions in cache.
    """

    # pylint: disable=no-method-argument
    _cache = Redis(host=REDIS_HOST, port=REDIS_PORT)
    # TODO: Create all data segments and getters to them using classproperty
    # _segments = [
    #     _DataSegment(
    #         name="",
    #         cache=_cache,
    #         data=dict()
    #     )
    # ]
