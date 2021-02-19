"""
Control system's common functionalities.
"""
from ..constants.control import NORMALISATION_PRECISION


def normalise(value: float, current_min: float, current_max: float, intended_min: float, intended_max: float) -> float:
    """
    Normalise a value to fit within a given range, knowing its actual range.

    Uses MinMax normalisation.
    """
    if current_min == current_max or intended_min == intended_max:
        raise ValueError("Minimum and maximum (both current and intended) must not be equal")
    if not current_max >= value >= current_min:
        raise ValueError(f"Value {value} is not be between {current_min} and {current_max}")

    return round(intended_min + (value - current_min) * (intended_max - intended_min) / (current_max - current_min),
                 NORMALISATION_PRECISION)
