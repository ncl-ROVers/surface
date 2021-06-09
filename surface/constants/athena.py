"""
Data manager constants.
"""
import os
from ..enums import ConnectionStatus, DrivingMode
from .control import THRUSTER_IDLE, GRIPPER_IDLE, CORD_IDLE, CONTROL_NORM_IDLE
from .control import CONTROL_AUTONOMOUS_NAME, CONTROL_MANUAL_NAME, CONTROL_MANAGER_NAME

# Declare redis settings - use .env file to override the defaults
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Declare the name of the driving mode key
RK_CONTROL_DRIVING_MODE = "driving-mode"

# Declare connection keys
RK_CONNECTION_SURFACE_PI = "surface-pi"

# Declare data dictionaries (that will be stored in cache) with their defaults (RK stands for Redis Key)
# Connection statuses between various components of the vehicle
DATA_CONNECTIONS = {
    RK_CONNECTION_SURFACE_PI: ConnectionStatus.DISCONNECTED.value
}
# Data received from Raspberry Pi
DATA_RECEIVED = {
    "A_A": False,
    "A_B": False,
    "S_A": 0,
    "S_B": 0
}
# Data that will be sent to Raspberry Pi
DATA_TRANSMISSION = {
    "T_HFP": THRUSTER_IDLE,
    "T_HFS": THRUSTER_IDLE,
    "T_HAP": THRUSTER_IDLE,
    "T_HAS": THRUSTER_IDLE,
    "T_VFP": THRUSTER_IDLE,
    "T_VFS": THRUSTER_IDLE,
    "T_VAP": THRUSTER_IDLE,
    "T_VAS": THRUSTER_IDLE,
    "T_M": THRUSTER_IDLE,
    "M_G": GRIPPER_IDLE,
    "M_C": CORD_IDLE
}
# Autonomous, manual, and merged control system data
DATA_CONTROL = {
    CONTROL_MANAGER_NAME + "-yaw": CONTROL_NORM_IDLE,
    CONTROL_MANAGER_NAME + "-pitch": CONTROL_NORM_IDLE,
    CONTROL_MANAGER_NAME + "-roll": CONTROL_NORM_IDLE,
    CONTROL_MANAGER_NAME + "-sway": CONTROL_NORM_IDLE,
    CONTROL_MANAGER_NAME + "-surge": CONTROL_NORM_IDLE,
    CONTROL_MANAGER_NAME + "-heave": CONTROL_NORM_IDLE,
    CONTROL_MANUAL_NAME + "-yaw": CONTROL_NORM_IDLE,
    CONTROL_MANUAL_NAME + "-pitch": CONTROL_NORM_IDLE,
    CONTROL_MANUAL_NAME + "-roll": CONTROL_NORM_IDLE,
    CONTROL_MANUAL_NAME + "-sway": CONTROL_NORM_IDLE,
    CONTROL_MANUAL_NAME + "-surge": CONTROL_NORM_IDLE,
    CONTROL_MANUAL_NAME + "-heave": CONTROL_NORM_IDLE,
    CONTROL_AUTONOMOUS_NAME + "-yaw": CONTROL_NORM_IDLE,
    CONTROL_AUTONOMOUS_NAME + "-pitch": CONTROL_NORM_IDLE,
    CONTROL_AUTONOMOUS_NAME + "-roll": CONTROL_NORM_IDLE,
    CONTROL_AUTONOMOUS_NAME + "-sway": CONTROL_NORM_IDLE,
    CONTROL_AUTONOMOUS_NAME + "-surge": CONTROL_NORM_IDLE,
    CONTROL_AUTONOMOUS_NAME + "-heave": CONTROL_NORM_IDLE,
    RK_CONTROL_DRIVING_MODE: DrivingMode.MANUAL.value
}
# Other, un-classified data
DATA_MISCELLANEOUS = {

}
