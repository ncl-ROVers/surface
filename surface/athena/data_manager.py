"""
Data manager module for dispatching information to different components of the vehicle.
"""
from redis import Redis
from ..utils import classgetter
from ..constants.athena import REDIS_HOST, REDIS_PORT
from ..constants.athena import DATA_CONNECTIONS, DATA_CONTROL, DATA_MISCELLANEOUS, DATA_RECEIVED, DATA_TRANSMISSION
from .data_segment import DataSegment


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
        DataSegment(
            name="connections",
            cache=_cache,
            data=DATA_CONNECTIONS
        ),
        DataSegment(
            name="received",
            cache=_cache,
            data=DATA_RECEIVED
        ),
        DataSegment(
            name="transmission",
            cache=_cache,
            data=DATA_TRANSMISSION
        ),
        DataSegment(
            name="control",
            cache=_cache,
            data=DATA_CONTROL
        ),
        DataSegment(
            name="miscellaneous",
            cache=_cache,
            data=DATA_MISCELLANEOUS
        )
    ]

    # Type hint return types of the segments to trick pylint, as it doesn't understand how descriptors work
    # pylint: disable = function-redefined
    connections: DataSegment
    received: DataSegment
    transmission: DataSegment
    control: DataSegment
    miscellaneous: DataSegment

    @classgetter
    def connections() -> DataSegment:
        """
        Fetch `connections` data.
        """
        return DataManager._segments[0]

    @classgetter
    def received() -> DataSegment:
        """
        Fetch `received` data.
        """
        return DataManager._segments[1]

    @classgetter
    def transmission() -> DataSegment:
        """
        Fetch `transmission` data.
        """
        return DataManager._segments[2]

    @classgetter
    def control() -> DataSegment:
        """
        Fetch `control` data.
        """
        return DataManager._segments[3]

    @classgetter
    def miscellaneous() -> DataSegment:
        """
        Fetch `miscellaneous` data.
        """
        return DataManager._segments[4]
