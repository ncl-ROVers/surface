"""
Surface control station execution file.
"""
import os
import sys
import time

# Make sure a local raspberry-pi package can be found and overrides any installed versions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

# pylint: disable = wrong-import-position
from surface.networking import Connection
from surface.control import ControlManager, ManualController
from surface.enums import ConnectionStatus

if __name__ == '__main__':
    control_manager_pid = ControlManager().start()
    manual_controller_pid = ManualController().start()
    connection = Connection()

    while True:
        status = connection.status

        if status == ConnectionStatus.DISCONNECTED:
            connection.connect()
        elif status == ConnectionStatus.IDLE:
            connection.reconnect()

        time.sleep(1)
