"""
Wrapper class around the normalised motion values.
"""
from ..constants.control import CONTROL_NORM_MAX, CONTROL_NORM_MIN, CONTROL_NORM_IDLE
from ..exceptions import ControlSystemException


class Motion:
    """
    Float between some specific values, with some associated string name.

    They are used for finer data passing between the software components.
    """

    def __init__(self, name: str):
        self._name = name
        self._value = CONTROL_NORM_IDLE

    @property
    def name(self) -> str:
        """
        Get the string key of the motion.
        """
        return self._name

    @property
    def value(self) -> float:
        """
        Get normalised float value.
        """
        return self._value

    @value.setter
    def value(self, value: float):
        """
        Any floats within the motion must be normalised into the expected min/max.
        """
        if CONTROL_NORM_MIN > value > CONTROL_NORM_MAX:
            raise ControlSystemException(f"{value} isn't normalised (between {CONTROL_NORM_MIN} "
                                         f"and {CONTROL_NORM_MAX} inclusive)")
        self._value = value
