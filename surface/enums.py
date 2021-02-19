"""
Enumerations.
"""
from enum import Enum


class DrivingMode(Enum):
    """
    Control mode of the ROV.

    Each mode corresponds to the following behaviour:

        - Manual for game pad controlling
        - Autonomous for running fully autonomous control algorithms
        - Assisted for easier, manual control of the vehicle

    """

    MANUAL = 0
    AUTONOMOUS = 1
    ASSISTED = 2


class ConnectionStatus(Enum):
    """
    Status of the data exchange process between some server and some client.

    The general lifecycle of each connection is as follows:

        - Disconnected
        - Connecting
        - Connected
        - Idle (relevant to TCP communication - flow stopped but socket's still open)
        - Disconnecting

    The connection statuses will represent connections between all networking elements of the ROV.
    """

    CONNECTED = 0
    DISCONNECTED = 1
    CONNECTING = 2
    DISCONNECTING = 3
    IDLE = 4
