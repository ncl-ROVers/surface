"""
"Joint" control model capable of merging data from several driving modes.
"""
from .data_manager import DataManager
from .enums import DrivingMode
from .model import ControlModel
from .converter import Converter
from .constants import DATA_CONTROL, CONTROL_MANAGER_NAME, CONTROL_MANUAL_NAME, CONTROL_AUTONOMOUS_NAME
from .converter import CONTROL_NORM_IDLE


class ControlManager(ControlModel):
    """
    Producer of the final collection of vehicle motions.

    The collection is created by merging several data from several driving modes:

        - Autonomous
        - Manual
        - Assisted (autonomous with manual)

    Additionally, upon each update, the transmission data is updated with hardware-specific control values.
    """

    def __init__(self):
        """
        As part of init, three dictionaries must be created.

            - Manual, containing keys and default values of manual control
            - Autonomous, containing keys and default values of autonomous control
            - Converted, containing hardware ready values which will be sent to the ROV

        The dictionaries will be modified at runtime.
        """
        super().__init__(CONTROL_MANAGER_NAME)
        control_data_items = DATA_CONTROL.items()
        self._manual = {key: value for key, value in control_data_items if key.startswith(CONTROL_MANUAL_NAME)}
        self._autonomous = {key: value for key, value in control_data_items if key.startswith(CONTROL_AUTONOMOUS_NAME)}
        self._converted = dict()

    def update(self, *args, **kwargs):
        """
        Four-step process of deriving the final vehicle's behaviour.
        """
        self._pull()
        self._merge()
        self._convert()
        self.push()

    def _pull(self):
        """
        Populate manual and autonomous dictionaries with up-to-date control data.
        """
        self._manual = DataManager.control.fetch(self._manual.keys())
        self._autonomous = DataManager.control.fetch(self._manual.keys())

    def _merge(self):
        """
        Produce final motions depending on the driving mode.
        """
        mode = self.mode

        if mode == DrivingMode.MANUAL:
            data = self._manual
        elif mode == DrivingMode.AUTONOMOUS:
            data = self._autonomous
        else:
            data = {key: self._manual[key] if self._manual[key] != CONTROL_NORM_IDLE else self._autonomous[key]
                    for key in self._manual}

        self.motions = {key.split("-")[-1]: value for key, value in data.items()}

    def _convert(self):
        """
        Convert motions to the hardware-specific values.
        """
        self._converted = Converter.convert(self.motions)

    def push(self):
        """
        Update relevant DataManager data - for control and for transmission.
        """
        super().push()
        DataManager.transmission.update(self._converted)
