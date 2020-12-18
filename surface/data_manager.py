"""
Data manager module for dispatching information to different components of the vehicle.
"""
from typing import Iterable
import msgpack
from msgpack import UnpackException, PackException
from redis import Redis, RedisError
from .utils import logger, classproperty
from .constants import REDIS_HOST, REDIS_PORT
from .constants import DATA_CONNECTIONS, DATA_CONTROL, DATA_MISCELLANEOUS, DATA_RECEIVED, DATA_TRANSMISSION
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
            for key, value in data.items():
                redis_key = self._build_redis_key(key)
                if self._cache.exists(redis_key):
                    logger.warning(f"Key {key} already existed at the initialisation of data segment {self._name}, "
                                   f"and will get overridden")
                self._cache.set(redis_key, msgpack.packb(value))
        except (RedisError, PackException) as ex:
            raise DataManagerException(f"Failed to initialise the data segment {self._name}") from ex

    def __getitem__(self, key):
        """
        Retrieve an item from the cache.

        `DataManagerException` will be thrown if the key wasn't registered at `__init__`, or in case of Redis and bytes
        conversion errors.
        """
        if key not in self._keys:
            raise DataManagerException(f"Failed to retrieve value using key {key} - key not registered")

        redis_key = self._build_redis_key(key)
        try:
            return msgpack.unpackb(self._cache.get(redis_key))
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
            self._cache.set(redis_key, msgpack.packb(value))
        except (RedisError, PackException) as ex:
            raise DataManagerException(f"Failed to save value {value} using key {key}") from ex

    @property
    def all(self) -> dict:
        """
        Retrieve all stored (key, value) pairs.

        `DataManagerException` will be thrown in case of `__getitem__` errors.
        """
        return {key: self.__getitem__(key) for key in self._keys}

    def fetch(self, keys: Iterable):
        """
        Retrieve a subset of all stored (key, value) pairs.

        `DataManagerException` will be thrown in case of `__getitem__` errors. Non-registered keys will be ignored.
        """
        data = dict()

        for key in keys:
            redis_key = self._build_redis_key(key)
            if not self._cache.exists(redis_key):
                logger.warning(f"Skipping fetching key {key} for data segment {self._name} - key not registered")
                continue
            data[key] = self.__getitem__(key)

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
        return self._name + "-" + key


# noinspection PyMethodParameters
class DataManager:
    """
    Handle creation of each data segment and access to it.

    Currently the segments are as follows:

        - connections - for monitoring network connection to each component
        - received - for data received from the ROV
        - transmission - for data that will be sent to the ROV
        - control - for all control system information
        - miscellaneous - for other, un-classified data

    You can retrieve each segment by using the associated descriptor, e.g.:

        print(DataManager.transmission.all)

    Keep in mind that each segment MUST have a unique name to avoid key collisions in cache.
    """

    # pylint: disable=no-method-argument
    _cache = Redis(host=REDIS_HOST, port=REDIS_PORT)
    _segments = [
        _DataSegment(
            name="connections",
            cache=_cache,
            data=DATA_CONNECTIONS
        ),
        _DataSegment(
            name="received",
            cache=_cache,
            data=DATA_RECEIVED
        ),
        _DataSegment(
            name="transmission",
            cache=_cache,
            data=DATA_TRANSMISSION
        ),
        _DataSegment(
            name="control",
            cache=_cache,
            data=DATA_CONTROL
        ),
        _DataSegment(
            name="miscellaneous",
            cache=_cache,
            data=DATA_MISCELLANEOUS
        )
    ]

    @classproperty
    def connections() -> _DataSegment:
        """
        Fetch `connections` data.
        """
        return DataManager._segments[0]

    @classproperty
    def received() -> _DataSegment:
        """
        Fetch `received` data.
        """
        return DataManager._segments[1]

    @classproperty
    def transmission() -> _DataSegment:
        """
        Fetch `transmission` data.
        """
        return DataManager._segments[2]

    @classproperty
    def control() -> _DataSegment:
        """
        Fetch `control` data.
        """
        return DataManager._segments[3]

    @classproperty
    def miscellaneous() -> _DataSegment:
        """
        Fetch `miscellaneous` data.
        """
        return DataManager._segments[4]
