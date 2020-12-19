"""
TODO
"""
import msgpack
from msgpack import PackException
from socket import socket, SHUT_RDWR
from multiprocessing import Process
from threading import Thread
from .utils import logger
from .constants import RK_CONNECTION_SURFACE_PI, CONNECTION_IP, CONNECTION_PORT, CONNECTION_DATA_SIZE
from .data_manager import DataManager
from .enums import ConnectionStatus
from .exceptions import NetworkingException


# noinspection PyMethodParameters
class Connection:
    """
    todo
    """
    def __init__(self):
        """
        todo
        """
        self._ip = CONNECTION_IP
        self._port = CONNECTION_PORT
        self._data_size = CONNECTION_DATA_SIZE
        self._address = self._ip, self._port
        self._socket = self._new_socket()
        self._communication_process = self._new_process()

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

    @staticmethod
    def _new_socket() -> socket:
        """
        todo
        """
        return socket()

    def _new_process(self) -> Process:
        """
        todo
        """
        return Process(target=self._communicate)

    def connect(self):
        """
        todo
        """
        if self.status != ConnectionStatus.DISCONNECTED:
            logger.error(f"Can't connect to {self._ip}:{self._port} - not disconnected (status is {self.status})")
            return

        logger.info(f"Connecting to {self._ip}:{self._port}")
        self.status = ConnectionStatus.CONNECTING

        # Launch blocking operations in a separate thread
        Thread(target=self._connect_threaded).start()

    def _connect_threaded(self):
        """
        todo
        """
        try:
            self._socket.connect(self._address)
            self._communication_process.start()
            self.status = ConnectionStatus.CONNECTED
            logger.info(f"Connected to {self._ip}:{self._port}")
        except (ConnectionError, OSError):
            logger.exception(f"Failed to connect safely")
            self.status = ConnectionStatus.DISCONNECTED
            self._cleanup(ignore_errors=True)

    def _communicate(self):
        """
        todo
        """
        while True:
            try:
                # Send the data to the server and retrieve immediatelly after (2-way-communication)
                self._socket.sendall(DataManager.transmission.all)
                received_data = self._socket.recv(self._data_size)

                # Exit if connection closed by server
                if not received_data:
                    logger.info(f"Communication with {self._ip}:{self._port} ended by the server")
                    break

                # Quit on any incorrectly formatted data
                try:
                    received_data = msgpack.unpackb(received_data.decode("utf-8").strip())
                except (UnicodeError, PackException):
                    logger.exception(f"Failed to unpack the following data: {received_data}")
                    break

                # Only handle valid, non-empty data
                if received_data and isinstance(received_data, dict):
                    DataManager.received.update(received_data)

            except (ConnectionError, OSError):
                logger.exception(f"An error occurred while communicating with the server")
                break

    def disconnect(self):
        """
        TODO
        """
        if self.status != ConnectionStatus.CONNECTED:
            logger.error(f"Can't disconnect from {self._ip}:{self._port} - not connected (status is {self.status})")
            return

        logger.info(f"Disconnecting from {self._ip}:{self._port}")
        self.status = ConnectionStatus.DISCONNECTING

        try:
            self._cleanup()
            logger.info(f"Disconnected from {self._ip}:{self._port}")
        except (ConnectionError, OSError):
            logger.exception(f"Failed to disconnect safely")
            self._cleanup(ignore_errors=True)

        # Set the disconnected status regardless of what happened above, to avoid deadlocking
        self.status = ConnectionStatus.DISCONNECTED

    def _cleanup(self, ignore_errors: bool = False):
        """
        todo
        """
        try:
            if self._communication_process.is_alive():
                self._communication_process.terminate()
            self._communication_process = self._new_process()
            self._socket.shutdown(SHUT_RDWR)
            self._socket.close()
            self._socket = self._new_socket()
        except (ConnectionError, OSError) as ex:
            if ignore_errors:
                logger.debug(f"Ignoring connection cleanup error - {ex}")
            else:
                raise NetworkingException(f"Failed to cleanup the connection") from ex

    def reconnect(self):
        """
        todo
        """
        logger.info(f"Reconnecting to {self._ip}:{self._port}")
        self.disconnect()
        self.connect()
