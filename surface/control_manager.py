"""
todo
"""
from .data_manager import DataManager
from .enums import DrivingMode
from .model import ControlModel
from .converter import Converter
from .constants import CONTROL_MANAGER_NAME, RK_CONTROL_DRIVING_MODE


class ControlManager(ControlModel):
    """
    todo
    """
    def __init__(self):
        super().__init__(CONTROL_MANAGER_NAME)
        self._manual = dict()
        self._autonomous = dict()
        self._converted = dict()

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

    def _merge(self):
        """
        todo
        """

    def _convert(self):
        """
        todo
        """
        self._converted = Converter.convert(self.motions)
