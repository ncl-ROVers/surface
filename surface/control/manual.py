"""
Manual driving control model.
"""
from multiprocessing import Process
from inputs import InputEvent
from .model import ControlModel
from .common import normalise
from ..constants.control import GAME_PAD, DEAD_ZONE, CONTROL_NORM_IDLE, CONTROL_NORM_MIN, CONTROL_NORM_MAX
from ..constants.control import HARDWARE_AXIS_MAX, HARDWARE_AXIS_MIN, HARDWARE_TRIGGER_MAX, HARDWARE_TRIGGER_MIN
from ..constants.control import INTENDED_AXIS_MAX, INTENDED_AXIS_MIN, INTENDED_TRIGGER_MAX, INTENDED_TRIGGER_MIN
from ..enums import DrivingMode
from ..utils import logger
from ..exceptions import ControlSystemException

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


def _normalise_axis(value: int) -> float:
    """
    Normalise an axis value passed from the hardware.

    Additionally, make sure that values low enough are considered 0, to avoid jitter.
    """
    value = 0 if -DEAD_ZONE < value < DEAD_ZONE else value
    return normalise(value, HARDWARE_AXIS_MIN, HARDWARE_AXIS_MAX, INTENDED_AXIS_MIN, INTENDED_AXIS_MAX)


def _normalise_trigger(value: int) -> float:
    """
    Normalise a trigger value passed from the hardware.
    """
    return normalise(value, HARDWARE_TRIGGER_MIN, HARDWARE_TRIGGER_MAX, INTENDED_TRIGGER_MIN, INTENDED_TRIGGER_MAX)


class ManualController(ControlModel):
    """
    Control the vehicle by using the game pad.

    Most generally, the controller's state is first recorded, and then associated callback functions are called if the
    vehicle's motion must be recalculated.
    """

    def __init__(self):
        super().__init__("manual")

        if not GAME_PAD:
            logger.error("Failed to detect the game controller")
            return

        self._left_axis_x = CONTROL_NORM_IDLE
        self._left_axis_y = CONTROL_NORM_IDLE
        self._right_axis_x = CONTROL_NORM_IDLE
        self._right_axis_y = CONTROL_NORM_IDLE
        self._left_trigger = CONTROL_NORM_IDLE
        self._right_trigger = CONTROL_NORM_IDLE
        self._hat_x = CONTROL_NORM_IDLE
        self._hat_y = CONTROL_NORM_IDLE
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

        self._process = Process(target=self._run, name="Manual Controller")

    @property
    def left_axis_x(self) -> float:
        """
        Get state of left joystick's X-axis.
        """
        return self._left_axis_x

    @left_axis_x.setter
    def left_axis_x(self, value: int):
        """
        Set state of left joystick's X-axis.
        """
        self._left_axis_x = _normalise_axis(value)

    @property
    def left_axis_y(self) -> float:
        """
        Get state of left joystick's Y-axis.
        """
        return self._left_axis_y

    @left_axis_y.setter
    def left_axis_y(self, value: int):
        """
        Set state of left joystick's Y-axis.
        """
        self._left_axis_y = _normalise_axis(value)
        self._update_surge()

    @property
    def right_axis_x(self) -> float:
        """
        Get state of right joystick's X-axis.
        """
        return self._right_axis_x

    @right_axis_x.setter
    def right_axis_x(self, value: int):
        """
        Set state of right joystick's X-axis.
        """
        self._right_axis_x = _normalise_axis(value)
        self._update_sway()

    @property
    def right_axis_y(self) -> float:
        """
        Get state of right joystick's Y-axis.
        """
        return self._right_axis_y

    @right_axis_y.setter
    def right_axis_y(self, value: int):
        """
        Set state of right joystick's Y-axis.
        """
        self._right_axis_y = _normalise_axis(value)
        self._update_pitch()

    @property
    def left_trigger(self) -> float:
        """
        Get state of left joystick's trigger.
        """
        return self._left_trigger

    @left_trigger.setter
    def left_trigger(self, value: int):
        """
        Set state of left joystick's trigger.
        """
        self._left_trigger = _normalise_trigger(value)
        self._update_yaw()

    @property
    def right_trigger(self) -> float:
        """
        Get state of right joystick's trigger.
        """
        return self._right_trigger

    @right_trigger.setter
    def right_trigger(self, value: int):
        """
        Set state of right joystick's trigger.
        """
        self._right_trigger = _normalise_trigger(value)
        self._update_yaw()

    @property
    def hat_x(self) -> int:
        """
        Get state of joystick's horizontal hat.
        """
        return self._hat_x

    @hat_x.setter
    def hat_x(self, value: int):
        """
        Set state of joystick's horizontal hat.
        """
        self._hat_x = value
        self._update_cord()

    @property
    def hat_y(self) -> int:
        """
        Get state of joystick's vertical hat.
        """
        return self._hat_y

    @hat_y.setter
    def hat_y(self, value: int):
        """
        Set state of joystick's vertical hat.
        """
        self._hat_y = value
        self._update_micro_thruster()

    @property
    def button_a(self) -> bool:
        """
        Get state of joystick's button A.
        """
        return self._button_a

    @button_a.setter
    def button_a(self, value: bool):
        """
        Set state of joystick's button A.
        """
        self._button_a = value
        self._update_gripper()

    @property
    def button_b(self) -> bool:
        """
        Get state of joystick's button B.
        """
        return self._button_b

    @button_b.setter
    def button_b(self, value: bool):
        """
        Set state of joystick's button B.
        """
        self._button_b = value
        self._update_roll()

    @property
    def button_x(self) -> bool:
        """
        Get state of joystick's button X.
        """
        return self._button_x

    @button_x.setter
    def button_x(self, value: bool):
        """
        Set state of joystick's button X.
        """
        self._button_x = value
        self._update_roll()

    @property
    def button_y(self) -> bool:
        """
        Get state of joystick's button Y.
        """
        return self._button_y

    @button_y.setter
    def button_y(self, value: bool):
        """
        Set state of joystick's button Y.
        """
        self._button_y = value
        self._update_gripper()

    @property
    def button_lb(self) -> bool:
        """
        Get state of joystick's button LB.
        """
        return self._button_lb

    @button_lb.setter
    def button_lb(self, value: bool):
        """
        Set state of joystick's button LB.
        """
        self._button_lb = value
        self._update_heave()

    @property
    def button_rb(self) -> bool:
        """
        Get state of joystick's button RB.
        """
        return self._button_rb

    @button_rb.setter
    def button_rb(self, value: bool):
        """
        Set state of joystick's button RB.
        """
        self._button_rb = value
        self._update_heave()

    @property
    def button_left_stick(self) -> bool:
        """
        Get state of joystick's left stick button.
        """
        return self._button_left_stick

    @button_left_stick.setter
    def button_left_stick(self, value: bool):
        """
        Set state of joystick's left stick button.
        """
        self._button_left_stick = value

    @property
    def button_right_stick(self) -> bool:
        """
        Get state of joystick's right stick button.
        """
        return self._button_right_stick

    @button_right_stick.setter
    def button_right_stick(self, value: bool):
        """
        Set state of joystick's right stick button.
        """
        self._button_right_stick = value

    @property
    def button_select(self) -> bool:
        """
        Get state of joystick's button SELECT.
        """
        return self._button_select

    @button_select.setter
    def button_select(self, value: bool):
        """
        Set state of joystick's button SELECT.
        """
        self._button_select = value
        self._update_mode()

    @property
    def button_start(self) -> bool:
        """
        Get state of joystick's button START.
        """
        return self._button_start

    @button_start.setter
    def button_start(self, value: bool):
        """
        Set state of joystick's button START.
        """
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
            self.yaw = CONTROL_NORM_IDLE

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
            self.roll = CONTROL_NORM_MAX
        elif self.button_x:
            self.roll = CONTROL_NORM_MIN
        else:
            self.roll = CONTROL_NORM_IDLE

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
            self.heave = CONTROL_NORM_MAX
        elif self.button_lb:
            self.heave = CONTROL_NORM_MIN
        else:
            self.heave = CONTROL_NORM_IDLE

    def _update_cord(self):
        """
        Cord is determined by the horizontal hat value.
        """
        if self.hat_x > 0:
            self.cord = CONTROL_NORM_MAX
        elif self.hat_x < 0:
            self.cord = CONTROL_NORM_MIN
        else:
            self.cord = CONTROL_NORM_IDLE

    def _update_gripper(self):
        """
        Gripper is determined by the buttons Y and A.
        """
        if self.button_y:
            self.gripper = CONTROL_NORM_MAX
        elif self.button_a:
            self.gripper = CONTROL_NORM_MIN
        else:
            self.gripper = CONTROL_NORM_IDLE

    def _update_micro_thruster(self):
        """
        Micro ROV thruster is determined by the vertical hat value.
        """
        if self.hat_y < 0:
            self.micro = CONTROL_NORM_MAX
        elif self.hat_y > 0:
            self.micro = CONTROL_NORM_MIN
        else:
            self.micro = CONTROL_NORM_IDLE

    def _update_mode(self):
        """
        Mode can be switched between manual and assisted only.

        Autonomous-only control must be enabled from other software components.
        """
        if self.button_start:
            if self.mode != DrivingMode.MANUAL:
                self.mode = DrivingMode.MANUAL
                self.motions = {
                    "yaw": CONTROL_NORM_IDLE,
                    "pitch": CONTROL_NORM_IDLE,
                    "roll": CONTROL_NORM_IDLE,
                    "sway": CONTROL_NORM_IDLE,
                    "surge": CONTROL_NORM_IDLE,
                    "heave": CONTROL_NORM_IDLE,
                    "cord": CONTROL_NORM_IDLE,
                    "gripper": CONTROL_NORM_IDLE,
                    "micro": CONTROL_NORM_IDLE,
                }
        elif self.button_select:
            self.mode = DrivingMode.ASSISTED

    def _dispatch_event(self, event: InputEvent):
        """
        Pass controller event to the model, given the hardware event ID and event value.
        """
        if event.code == "SYN_REPORT":
            return

        if event.code in DISPATCH_MAP:
            self.__setattr__(DISPATCH_MAP[event.code], event.state)
            self.update()
        else:
            logger.warning(f"Skipping event not registered in the dispatch map - {event.code}")

    def update(self, *args, **kwargs):
        """
        Push the motion data to the control manager.
        """
        self.push()

    def _run(self):
        """
        Target for the process spawning (wrapper method).
        """
        while True:
            self._dispatch_event(GAME_PAD.read()[0])

    def start(self) -> int:
        """
        Start the hardware readings in a separate process.

        PID is returned to properly cleanup the processes in the main execution loop.
        """
        if not GAME_PAD:
            raise ControlSystemException("Can't start the control system loop")

        self._process.start()
        logger.info(f"Controller reading process started, pid {self._process.pid}")
        return self._process.pid
