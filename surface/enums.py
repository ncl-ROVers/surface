"""
Enumerations used in several places within the application.
"""
from enum import Enum


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
