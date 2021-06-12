"""
Control system's constants.
"""
import inputs

# Controller must be defined outside of the class to allow seamless multiprocessing (otherwise serialisation fails)
GAME_PAD = inputs.devices.gamepads[0] if inputs.devices.gamepads else None

# Names of the control models
CONTROL_AUTONOMOUS_NAME = "autonomous"
CONTROL_MANUAL_NAME = "manual"
CONTROL_MANAGER_NAME = "manager"

# Precision of the normalisation function
NORMALISATION_PRECISION = 3

# Control's normal values
CONTROL_NORM_MAX = 1
CONTROL_NORM_IDLE = 0
CONTROL_NORM_MIN = -1

# Hardware values
THRUSTER_MAX = 1900
THRUSTER_IDLE = 1500
THRUSTER_MIN = 1100
GRIPPER_MAX = 1600
GRIPPER_IDLE = 1500
GRIPPER_MIN = 1400
CORD_MAX = 1600
CORD_IDLE = 1500
CORD_MIN = 1400

# Joystick control boundary - any values below are considered 0
DEAD_ZONE = 1025

# Hardware and the expected min/max values
HARDWARE_AXIS_MAX = 32767
HARDWARE_AXIS_MIN = -32768
HARDWARE_TRIGGER_MAX = 255
HARDWARE_TRIGGER_MIN = 0
INTENDED_AXIS_MAX = CONTROL_NORM_MAX
INTENDED_AXIS_MIN = CONTROL_NORM_MIN
INTENDED_TRIGGER_MAX = CONTROL_NORM_MAX
INTENDED_TRIGGER_MIN = CONTROL_NORM_IDLE
