"""
todo
"""
from .data_manager import DataManager
from .enums import DrivingMode
from .model import ControlModel
from .converter import Converter
from .constants import DATA_CONTROL, CONTROL_MANAGER_NAME, CONTROL_MANUAL_NAME, CONTROL_AUTONOMOUS_NAME
from .converter import CONTROL_NORM_IDLE


class ControlManager(ControlModel):
    """
    todo
    """
    def __init__(self):
        super().__init__(CONTROL_MANAGER_NAME)
        control_data_items = DATA_CONTROL.items()
        self._manual = {key: value for key, value in control_data_items if key.startswith(CONTROL_MANUAL_NAME)}
        self._autonomous = {key: value for key, value in control_data_items if key.startswith(CONTROL_AUTONOMOUS_NAME)}
        self._converted = dict()

    def update(self, *args, **kwargs):
        """
        todo
        """
        self._pull()
        self._merge()
        self._convert()
        self.push()

    def _pull(self):
        """
        todo
        """
        self._manual = DataManager.control.fetch(self._manual.keys())
        self._autonomous = DataManager.control.fetch(self._manual.keys())

    def _merge(self):
        """
        todo
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
        todo
        """
        self._converted = Converter.convert(self.motions)
