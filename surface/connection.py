"""
TODO
"""
import msgpack
import socket
from multiprocessing import Process
from .constants import RK_CONNECTION_SURFACE_PI, CONNECTION_IP, CONNECTION_PORT
from .data_manager import DataManager
from .enums import ConnectionStatus


# noinspection PyMethodParameters
class Connection:
    """
    todo
    """
    # pylint: disable=no-method-argument

    @property
    def status(self) -> ConnectionStatus:
        """
        todo
        """
        return ConnectionStatus(DataManager.connections[RK_CONNECTION_SURFACE_PI])

    @status.setter
    def status(self, value: ConnectionStatus):
        """
        todo
        """
        DataManager.connections[RK_CONNECTION_SURFACE_PI] = value

    def connect(self):
        pass

    def disconnect(self):
        pass

    def reconnect(self):
        pass

    def _new_socket(self):
        pass

    def _new_process(self):
        pass
