"""
todo
"""
import abc
from abc import ABC
from typing import Dict
from .data_manager import DataManager
from .motion import Motion


class ControlModel(ABC):
    """
    todo
    """

    def __init__(self, name: str):
        """
        todo
        """
        self._name = name
        self._yaw = Motion("yaw")
        self._pitch = Motion("pitch")
        self._roll = Motion("roll")
        self._sway = Motion("sway")
        self._surge = Motion("surge")
        self._heave = Motion("heave")

    @property
    def motions(self) -> Dict[str, Motion]:
        """
        todo
        """
        return {
            "yaw": self._yaw,
            "pitch": self._pitch,
            "roll": self._roll,
            "sway": self._sway,
            "surge": self._surge,
            "heave": self._heave
        }

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        """
        todo
        """

    def push(self):
        """
        todo
        """
        data = {"-".join((self._name, key)): value.value for key, value in self.motions.items()}
        DataManager.control.update(data)
