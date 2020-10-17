"""
Universal classes and other non-static constructs.
"""
import os
import json
import logging.config
from .constants import LOG_CONFIG_PATH, LOG_DIR, LOGGER_NAME


# noinspection PyPep8Naming
class classproperty:
    """
    Descriptor allowing declaring class-bound properties.

    Once used, you can declare a class property as follows:

        class SomeClass:

            @classproperty
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
