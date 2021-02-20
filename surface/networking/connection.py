"""
Connection module for exchanging data with the Raspberry Pi.
"""
from socket import socket, SHUT_RDWR
from multiprocessing import Process
from threading import Thread
import msgpack
from msgpack import UnpackException
from ..constants.networking import CONNECTION_IP, CONNECTION_PORT, CONNECTION_DATA_SIZE
from ..constants.athena import RK_CONNECTION_SURFACE_PI
from ..utils import logger
from ..athena import DataManager
from ..exceptions import NetworkingException
from ..enums import ConnectionStatus


# noinspection PyMethodParameters
class Connection:
    """
    Communicate with Raspberry Pi by establishing a 2-way data exchange via a TCP network.

    A connection is a non-enforced singleton featuring the following functionalities:

        - set and retrieve connection status
        - network data using a socket
        - connect to the server in a non-blocking manner
        - communicate with the server in a separate process
        - clean up resources

    Upon the communication process ending, the `IDLE` connection status will be set. The calling code must then handle
    this scenario, for example by `reconnect`-ing.
    """

    def __init__(self):
        self._ip = CONNECTION_IP
        self._port = CONNECTION_PORT
        self._data_size = CONNECTION_DATA_SIZE
        self._address = self._ip, self._port
        self._socket = self._new_socket()
        self._communication_process = self._new_process()

    @property
    def status(self) -> ConnectionStatus:
        """
        Retrieve current connection's state (process-independent).
        """
        return ConnectionStatus(DataManager.connections[RK_CONNECTION_SURFACE_PI])

    @status.setter
    def status(self, value: ConnectionStatus):
        """
        Set the connection's state (process-independent).
        """
        # pylint: disable = no-self-use
        DataManager.connections[RK_CONNECTION_SURFACE_PI] = value.value

    @staticmethod
    def _new_socket() -> socket:
        """
        Build a new socket needed for networking purposes.
        """
        return socket()

    def _new_process(self) -> Process:
        """
        Create an new process needed for making communication a non-blocking, efficient operation.
        """
        return Process(target=self._communicate)

    def connect(self):
        """
        Connect to the server.

        Runs all connection methods in a separate thread, to avoid hanging the main thread on the blocking operations.
        """
        Thread(target=self._connect_threaded).start()

    def _connect_threaded(self):
        """
        Connect to the server and start the communication process.

        Connection may only happen if the client is currently disconnected.

        Connection failures are silent and will not cause any global exceptions to be raised.
        """
        if self.status != ConnectionStatus.DISCONNECTED:
            logger.warning(f"Can't connect to {self._ip}:{self._port} - not disconnected (status is {self.status})")
            return

        logger.info(f"Connecting to {self._ip}:{self._port}")
        self.status = ConnectionStatus.CONNECTING

        try:
            self._socket.connect(self._address)
            self._communication_process.start()
            self.status = ConnectionStatus.CONNECTED
            logger.info(f"Connected to {self._ip}:{self._port}")
        except OSError:
            logger.exception("Failed to connect safely")
            self.status = ConnectionStatus.DISCONNECTED
            self._cleanup(ignore_errors=True)

    def _communicate(self):
        """
        Exchange data with the server.

        Within the loop, the client sends the data first, and then waits for a response. Once the loop is exited, the
        `IDLE` status is set, and the calling code must detect and handle this on their own.
        """
        while True:
            try:
                # Send the data to the server and retrieve immediately after (2-way-communication)
                self._socket.sendall(msgpack.packb(DataManager.transmission.all()))
                received_data = self._socket.recv(self._data_size)

                # Exit if connection closed by server
                if not received_data:
                    logger.info(f"Communication with {self._ip}:{self._port} ended by the server")
                    break

                # Quit on any incorrectly formatted data
                try:
                    received_data = msgpack.unpackb(received_data)
                except UnpackException:
                    logger.exception(f"Failed to unpack the following data: {received_data}")
                    break

                # Only handle valid, non-empty data
                if received_data and isinstance(received_data, dict):
                    DataManager.received.update(received_data)

            except (UnpackException, OSError):
                logger.exception("An error occurred while communicating with the server")
                break

        # Once the communication has ended, the IDLE status will be set - should be detected and handled by the caller
        self.status = ConnectionStatus.IDLE

    def disconnect(self):
        """
        Disconnected from the server.

        Disconnection may only happen if the client is connected or idle.

        Disconnection failures are silent and will not cause any global exceptions to be raised.

        The `DISCONNECTED` status will always be set, regardless of whether the connection has been shut down properly
        or not. This is to avoid the client being unable to connect again in case of non-handled issues.
        """
        if self.status != ConnectionStatus.CONNECTED and self.status != ConnectionStatus.IDLE:
            logger.warning(f"Can't disconnect from {self._ip}:{self._port} - not connected or idle "
                           f"(status is {self.status})")
            return

        logger.info(f"Disconnecting from {self._ip}:{self._port}")
        self.status = ConnectionStatus.DISCONNECTING

        try:
            self._cleanup()
            logger.info(f"Disconnected from {self._ip}:{self._port}")
        except OSError:
            logger.exception("Failed to disconnect safely")
            self._cleanup(ignore_errors=True)

        # Set the disconnected status regardless of what happened above, to avoid deadlocking
        self.status = ConnectionStatus.DISCONNECTED

    def _cleanup(self, ignore_errors: bool = False):
        """
        Stop all components as well as recreate the socket and the communication process.
        """
        try:
            if self._communication_process.is_alive():
                self._communication_process.terminate()
            self._communication_process = self._new_process()
            self._socket.shutdown(SHUT_RDWR)
            self._socket.close()
            self._socket = self._new_socket()
        except OSError as ex:
            if ignore_errors:
                logger.debug(f"Ignoring connection cleanup error - {ex}")
            else:
                raise NetworkingException("Failed to cleanup the connection") from ex

    def reconnect(self):
        """
        Disconnect and connect again.
        """
        logger.info(f"Reconnecting to {self._ip}:{self._port}")
        self.disconnect()
        self.connect()
