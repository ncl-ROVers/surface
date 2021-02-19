"""
Universal classes and other non-static constructs.
"""
import os
import json
import logging.config
from .constants import LOG_CONFIG_PATH, LOG_DIR, LOGGER_NAME
from .constants import NORMALISATION_PRECISION


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


# noinspection PyPep8Naming
class classgetter:
    """
    Descriptor allowing declaring class-bound getters.

    Once used, you can declare a class getter as follows:

        class SomeClass:

            @classgetter
            def value():
                return 10

    and use it:

        print(SomeClass.value)  # prints "10"

    Note that you will need to add "# pylint: disable=no-method-argument" to disable linting, because pylint won't know
    that this descriptor allows defining methods with no `self` or `cls` arguments.
    """

    # pylint: disable=invalid-name

    def __init__(self, func):
        self._func = func

    def __get__(self, _obj, _type):
        return self._func()

    def __func__(self):
        return self._func


# Configure logging and create a new logger instance
with open(LOG_CONFIG_PATH) as f:
    log_config = json.loads(f.read())
    handlers = log_config["handlers"]
    for handler in handlers:
        handler_config = handlers[handler]
        if "filename" in handler_config:
            handler_config["filename"] = os.path.join(LOG_DIR, handler_config["filename"])
logging.config.dictConfig(log_config)
logger = logging.getLogger(LOGGER_NAME)
