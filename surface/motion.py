"""
todo
"""
from .exceptions import ControlSystemException
from .constants import CONTROL_NORM_MAX, CONTROL_NORM_MIN, CONTROL_NORM_IDLE


class Motion:
    """
    todo
    """

    def __init__(self, name: str):
        self._name = name
        self._value = CONTROL_NORM_IDLE

    @property
    def name(self) -> str:
        """
        todo
        """
        return self._name

    @property
    def value(self) -> float:
        """
        todo
        """
        return self._value

    @value.setter
    def value(self, value: float):
        """
        todo
        """
        if CONTROL_NORM_MIN > value > CONTROL_NORM_MAX:
            raise ControlSystemException(f"{value} isn't normalised (between -1 and 1 inclusive)")

        self._value = value
