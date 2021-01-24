"""
todo
"""
from multiprocessing import Process
import inputs
from inputs import InputEvent
from .utils import logger
from .model import ControlModel
from .constants import CONTROL_NORM_IDLE, CONTROL_NORM_MIN, CONTROL_NORM_MAX
from .utils import normalise
from .enums import DrivingMode
from .exceptions import ControlSystemException

# Create the hardware to class value dispatcher
DISPATCH_MAP = {
    "ABS_X": "left_axis_x",
    "ABS_Y": "left_axis_y",
    "ABS_RX": "right_axis_x",
    "ABS_RY": "right_axis_y",
    "ABS_Z": "left_trigger",
    "ABS_RZ": "right_trigger",
    "ABS_HAT0X": "hat_x",
    "ABS_HAT0Y": "hat_y",
    "BTN_SOUTH": "button_a",
    "BTN_EAST": "button_b",
    "BTN_WEST": "button_x",
    "BTN_NORTH": "button_y",
    "BTN_TL": "button_lb",
    "BTN_TR": "button_rb",
    "BTN_THUMBL": "button_left_stick",
    "BTN_THUMBR": "button_right_stick",
    "BTN_START": "button_select",
    "BTN_SELECT": "button_start"
}

# Declare the max and min values - the hardware and the expected ones
# TODO: This will have to be moved to the control system constants
DEAD_ZONE = 1025
HARDWARE_AXIS_MAX = 32767
HARDWARE_AXIS_MIN = -32768
HARDWARE_TRIGGER_MAX = 255
HARDWARE_TRIGGER_MIN = 0
INTENDED_AXIS_MAX = CONTROL_NORM_MAX
INTENDED_AXIS_MIN = CONTROL_NORM_MIN
INTENDED_TRIGGER_MAX = CONTROL_NORM_MAX
INTENDED_TRIGGER_MIN = CONTROL_NORM_IDLE

CONTROLLER = inputs.devices.gamepads[0] if inputs.devices.gamepads else None


def _normalise_axis(value: int) -> float:
    """
    Avoid using hardware-specific axis values.

    Additionally, make sure that values low enough are considered 0, to avoid jitter.
    """
    value = 0 if -DEAD_ZONE < value < DEAD_ZONE else value
    return normalise(value, HARDWARE_AXIS_MIN, HARDWARE_AXIS_MAX, INTENDED_AXIS_MIN, INTENDED_AXIS_MAX)


def _normalise_trigger(value: int) -> float:
    """
    Avoid using hardware-specific trigger values.
    """
    return normalise(value, HARDWARE_TRIGGER_MIN, HARDWARE_TRIGGER_MAX, INTENDED_TRIGGER_MIN, INTENDED_TRIGGER_MAX)


class ManualController(ControlModel):
    """
    todo
    """

    def __init__(self):
        super().__init__("manual")

        if not CONTROLLER:
            logger.error("Failed to detect the game controller")
            return

        self._left_axis_x = 0
        self._left_axis_y = 0
        self._right_axis_x = 0
        self._right_axis_y = 0
        self._left_trigger = 0
        self._right_trigger = 0
        self._hat_x = 0
        self._hat_y = 0
        self._button_a = False
        self._button_b = False
        self._button_x = False
        self._button_y = False
        self._button_lb = False
        self._button_rb = False
        self._button_left_stick = False
        self._button_right_stick = False
        self._button_select = False
        self._button_start = False

        self._process = Process(target=self._read, name="Controller")

    def __bool__(self):
        """
        todo
        """
        return CONTROLLER is not None

    @property
    def left_axis_x(self) -> int:
        return self._left_axis_x
    
    @left_axis_x.setter
    def left_axis_x(self, value: int):
        self._left_axis_x = _normalise_axis(value)
    
    @property
    def left_axis_y(self) -> int:
        return self._left_axis_y
    
    @left_axis_y.setter
    def left_axis_y(self, value: int):
        self._left_axis_y = _normalise_axis(value)
        self._update_surge()
    
    @property
    def right_axis_x(self) -> int:
        return self._right_axis_x
    
    @right_axis_x.setter
    def right_axis_x(self, value: int):
        self._right_axis_x = _normalise_axis(value)
        self._update_sway()
    
    @property
    def right_axis_y(self) -> int:
        return self._right_axis_y
    
    @right_axis_y.setter
    def right_axis_y(self, value: int):
        self._right_axis_y = _normalise_axis(value)
        self._update_pitch()
    
    @property
    def left_trigger(self) -> int:
        return self._left_trigger
    
    @left_trigger.setter
    def left_trigger(self, value: int):
        self._left_trigger = _normalise_trigger(value)
        self._update_yaw()

    @property
    def right_trigger(self) -> int:
        return self._right_trigger
    
    @right_trigger.setter
    def right_trigger(self, value: int):
        self._right_trigger = _normalise_trigger(value)
        self._update_yaw()

    @property
    def hat_x(self) -> int:
        return self._hat_x

    @hat_x.setter
    def hat_x(self, value: int):
        self._hat_x = value

    @property
    def hat_y(self) -> int:
        return self._hat_y

    @hat_y.setter
    def hat_y(self, value: int):
        self._hat_y = value

    @property
    def button_a(self) -> bool:
        return self._button_a
    
    @button_a.setter
    def button_a(self, value: bool):
        self._button_a = value
    
    @property
    def button_b(self) -> bool:
        return self._button_b
    
    @button_b.setter
    def button_b(self, value: bool):
        self._button_b = value
        self._update_roll()
    
    @property
    def button_x(self) -> bool:
        return self._button_x
    
    @button_x.setter
    def button_x(self, value: bool):
        self._button_x = value
        self._update_roll()
    
    @property
    def button_y(self) -> bool:
        return self._button_y
    
    @button_y.setter
    def button_y(self, value: bool):
        self._button_y = value

    @property
    def button_lb(self) -> bool:
        return self._button_lb

    @button_lb.setter
    def button_lb(self, value: bool):
        self._button_lb = value
        self._update_heave()

    @property
    def button_rb(self) -> bool:
        return self._button_rb

    @button_rb.setter
    def button_rb(self, value: bool):
        self._button_rb = value
        self._update_heave()

    @property
    def button_left_stick(self) -> bool:
        return self._button_left_stick

    @button_left_stick.setter
    def button_left_stick(self, value: bool):
        self._button_left_stick = value

    @property
    def button_right_stick(self) -> bool:
        return self._button_right_stick
    
    @button_right_stick.setter
    def button_right_stick(self, value: bool):
        self._button_right_stick = value
    
    @property
    def button_select(self) -> bool:
        return self._button_select
    
    @button_select.setter
    def button_select(self, value: bool):
        self._button_select = value
        self._update_mode()
    
    @property
    def button_start(self) -> bool:
        return self._button_start
    
    @button_start.setter
    def button_start(self, value: bool):
        self._button_start = value
        self._update_mode()

    def _update_yaw(self):
        """
        Yaw is determined by both triggers.
        """
        if self.right_trigger:
            self.yaw = self.right_trigger
        elif self.left_trigger:
            self.yaw = -self.left_trigger
        else:
            self.yaw = 0

    def _update_pitch(self):
        """
        Pitch is determined by the vertical right axis.
        """
        self.pitch = self.right_axis_y

    def _update_roll(self):
        """
        Roll is determined by the buttons X and B.
        """
        if self.button_b:
            self.roll = 1.0
        elif self.button_x:
            self.roll = -1.0
        else:
            self.roll = 0

    def _update_sway(self):
        """
        Sway is determined by the horizontal right axis.
        """
        self.sway = self.right_axis_x

    def _update_surge(self):
        """
        Surge is determined by the vertical left axis.
        """
        self.surge = self.left_axis_y

    def _update_heave(self):
        """
        Heave is determined by the buttons RB and LB.
        """
        if self.button_rb:
            self.heave = 1.0
        elif self.button_lb:
            self.heave = -1.0
        else:
            self.heave = 0

    def _update_mode(self):
        """
        todo
        """
        print("A")
        print(self.mode)
        print("B")
        if self.button_start:
            if self.mode != DrivingMode.MANUAL:
                self.mode = DrivingMode.MANUAL
                self.motions = {
                    "yaw": 0.0,
                    "pitch": 0.0,
                    "roll": 0.0,
                    "sway": 0.0,
                    "surge": 0.0,
                    "heave": 0.0
                }
        elif self.button_select:
            self.mode = DrivingMode.ASSISTED

    def _dispatch_event(self, event: InputEvent):
        """
        todo
        """
        if event.code == "SYN_REPORT":
            return

        if event.code in DISPATCH_MAP:
            self.__setattr__(DISPATCH_MAP[event.code], event.state)
            self.update()
        else:
            logger.warning(f"Skipping event not registered in the dispatch map - {event.code}")

    def update(self):
        """
        todo
        """
        print(self.motions)
        self.push()

    def _read(self):
        """
        Wrapper method used as a target for the process spawning.
        """
        while True:
            self._dispatch_event(CONTROLLER.read()[0])

    def start(self) -> int:
        """
        Method used to start the hardware readings in a separate process.

        :return: -1 on errors or process id
        """
        if not self:
            raise ControlSystemException("Can't start the control system loop")
        else:
            self._process.start()
            logger.info(f"Controller reading process started, pid {self._process.pid}")
            return self._process.pid
