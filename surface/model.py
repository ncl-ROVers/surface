"""
todo
"""
import abc
from abc import ABC
from typing import Dict, Set
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

    @motions.setter
    def motions(self, values: dict):
        """
        todo - mention explicit update instead of setattrr to get meaningful errors
        """
        self._yaw = values["yaw"]
        self._pitch = values["pitch"]
        self._roll = values["roll"]
        self._sway = values["sway"]
        self._surge = values["surge"]
        self._heave = values["heave"]

    @property
    def keys(self) -> Set[str]:
        """
        todo get manager keys
        """
        return {self._build_key(key) for key in self.motions.keys()}

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        """
        todo - abstrac method, update self.motions here, and self.push at the end
        """

    def push(self):
        """
        todo
        """
        data = {self._build_key(key): value.value for key, value in self.motions.items()}
        DataManager.control.update(data)

    def _build_key(self, key: str) -> str:
        """
        todo
        """
        return "-".join((self._name, key))
