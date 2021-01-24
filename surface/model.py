"""
todo
"""
import abc
from abc import ABC
from typing import Dict, Set
from .data_manager import DataManager
from .motion import Motion
from .constants import RK_CONTROL_DRIVING_MODE
from .enums import DrivingMode


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
    def yaw(self) -> float:
        return self._yaw.value

    @yaw.setter
    def yaw(self, value: float):
        self._yaw.value = value

    @property
    def pitch(self) -> float:
        return self._pitch.value

    @pitch.setter
    def pitch(self, value: float):
        self._pitch.value = value

    @property
    def roll(self) -> float:
        return self._roll.value

    @roll.setter
    def roll(self, value: float):
        self._roll.value = value

    @property
    def sway(self) -> float:
        return self._sway.value

    @sway.setter
    def sway(self, value: float):
        self._sway.value = value

    @property
    def surge(self) -> float:
        return self._surge.value

    @surge.setter
    def surge(self, value: float):
        self._surge.value = value

    @property
    def heave(self) -> float:
        return self._heave.value

    @heave.setter
    def heave(self, value: float):
        self._heave.value = value

    @property
    def mode(self) -> DrivingMode:
        """
        todo
        """
        return DrivingMode(DataManager.control[RK_CONTROL_DRIVING_MODE])

    @mode.setter
    def mode(self, value: DrivingMode):
        """
        todo
        """
        # pylint: disable = no-self-use
        DataManager.control[RK_CONTROL_DRIVING_MODE] = value.value

    @property
    def motions(self) -> Dict[str, float]:
        """
        todo
        """
        return {
            "yaw": self.yaw,
            "pitch": self.pitch,
            "roll": self.roll,
            "sway": self.sway,
            "surge": self.surge,
            "heave": self.heave
        }

    @motions.setter
    def motions(self, values: dict):
        """
        todo - mention explicit update instead of setattrr to get meaningful errors
        """
        self.yaw = values["yaw"]
        self.pitch = values["pitch"]
        self.roll = values["roll"]
        self.sway = values["sway"]
        self.surge = values["surge"]
        self.heave = values["heave"]

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
        data = {self._build_key(key): value for key, value in self.motions.items()}
        DataManager.control.update(data)

    def _build_key(self, key: str) -> str:
        """
        todo
        """
        return "-".join((self._name, key))
