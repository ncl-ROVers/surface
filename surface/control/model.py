"""
Base class allowing specifying custom control models.
"""
import abc
from abc import ABC
from typing import Dict, Set
from .motion import Motion
from ..enums import DrivingMode
from ..athena import DataManager
from ..constants.athena import RK_CONTROL_DRIVING_MODE


class ControlModel(ABC):
    """
    Abstract base class (ABC) defining a collection of vehicle motions and data manager related methods.

    Upon inheriting from it, the `update` method should be implemented according to the instructions.
    """

    def __init__(self, name: str):
        """
        Name will be used to create the control system's data manager keys.
        """
        self._name = name
        self._yaw = Motion("yaw")
        self._pitch = Motion("pitch")
        self._roll = Motion("roll")
        self._sway = Motion("sway")
        self._surge = Motion("surge")
        self._heave = Motion("heave")
        self._cord = Motion("cord")
        self._gripper = Motion("gripper")
        self._micro = Motion("micro")

    @property
    def yaw(self) -> float:
        """
        Get current yaw.
        """
        return self._yaw.value

    @yaw.setter
    def yaw(self, value: float):
        """
        Set current yaw.
        """
        self._yaw.value = value

    @property
    def pitch(self) -> float:
        """
        Get current pitch.
        """
        return self._pitch.value

    @pitch.setter
    def pitch(self, value: float):
        """
        Set current pitch.
        """
        self._pitch.value = value

    @property
    def roll(self) -> float:
        """
        Get current roll.
        """
        return self._roll.value

    @roll.setter
    def roll(self, value: float):
        """
        Set current roll.
        """
        self._roll.value = value

    @property
    def sway(self) -> float:
        """
        Get current sway.
        """
        return self._sway.value

    @sway.setter
    def sway(self, value: float):
        """
        Set current sway.
        """
        self._sway.value = value

    @property
    def surge(self) -> float:
        """
        Get current surge.
        """
        return self._surge.value

    @surge.setter
    def surge(self, value: float):
        """
        Set current surge.
        """
        self._surge.value = value

    @property
    def heave(self) -> float:
        """
        Get current heave.
        """
        return self._heave.value

    @heave.setter
    def heave(self, value: float):
        """
        Set current heave.
        """
        self._heave.value = value

    @property
    def cord(self) -> float:
        """
        Get current cord value.
        """
        return self._cord.value

    @cord.setter
    def cord(self, value: float):
        """
        Set current cord value.
        """
        self._cord.value = value

    @property
    def gripper(self) -> float:
        """
        Get current gripper value.
        """
        return self._gripper.value

    @gripper.setter
    def gripper(self, value: float):
        """
        Set current gripper value.
        """
        self._gripper.value = value

    @property
    def micro(self) -> float:
        """
        Get current micro ROV thruster value.
        """
        return self._micro.value

    @micro.setter
    def micro(self, value: float):
        """
        Set current micro ROV thruster value.
        """
        self._micro.value = value

    @property
    def mode(self) -> DrivingMode:
        """
        Retrieve the current driving mode from the data manager.
        """
        return DrivingMode(DataManager.control[RK_CONTROL_DRIVING_MODE])

    @mode.setter
    def mode(self, value: DrivingMode):
        """
        Set the driving mode in the data manager.
        """
        # pylint: disable = no-self-use
        DataManager.control[RK_CONTROL_DRIVING_MODE] = value.value

    @property
    def motions(self) -> Dict[str, float]:
        """
        Get a dictionary-based representation of vehicle's motions.
        """
        return {
            "yaw": self.yaw,
            "pitch": self.pitch,
            "roll": self.roll,
            "sway": self.sway,
            "surge": self.surge,
            "heave": self.heave,
            "cord": self.cord,
            "gripper": self.gripper,
            "micro": self.micro
        }

    @motions.setter
    def motions(self, values: dict):
        """
        Modify motions using passed dictionary.

        Direct assignment is used to get meaningful errors.
        """
        self.yaw = values["yaw"]
        self.pitch = values["pitch"]
        self.roll = values["roll"]
        self.sway = values["sway"]
        self.surge = values["surge"]
        self.heave = values["heave"]
        self.cord = values["cord"]
        self.gripper = values["gripper"]
        self.micro = values["micro"]

    @property
    def keys(self) -> Set[str]:
        """
        Get all data manager keys.
        """
        return {self._build_key(key) for key in self.motions}

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        """
        Abstract method, should be implemented upon inheritance.

        This is where self.motions should be updated. At the end, `self.push` method should be called to update the
        values in the data manager.
        """

    def push(self):
        """
        Upload the values to the data manager.
        """
        data = {self._build_key(key): value for key, value in self.motions.items()}
        DataManager.control.update(data)

    def _build_key(self, key: str) -> str:
        """
        Build data manager key given string key.

        For example, for "manual" control model and "yaw" key, the data manager key will be "manual-yaw".
        """
        return "-".join((self._name, key))
