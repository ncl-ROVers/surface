"""
Constants and other static values.
"""
import os
import dotenv
from .enums import ConnectionStatus, DrivingMode

# Declare paths to relevant folders - tests folder shouldn't be known here
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
SURFACE_DIR = os.path.join(ROOT_DIR, "surface")
RES_DIR = os.path.join(SURFACE_DIR, "res")
LOG_DIR = os.path.join(SURFACE_DIR, "log")

# Load the environment variables from the root folder and/or the resources folder
dotenv.load_dotenv(dotenv_path=os.path.join(ROOT_DIR, ".env"))
dotenv.load_dotenv(dotenv_path=os.path.join(RES_DIR, ".env"))

# Declare redis settings - use .env file to override the defaults
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Declare logging config - use .env file to override the defaults
LOG_CONFIG_PATH = os.getenv("LOG_CONFIG_PATH", os.path.join(RES_DIR, "log-config.json"))
LOGGER_NAME = os.getenv("LOGGER_NAME", "surface")

# Declare connection information - use .env file to override the defaults
CONNECTION_IP = os.getenv("CONNECTION_IP", "localhost")
CONNECTION_PORT = int(os.getenv("CONNECTION_PORT", "50000"))
CONNECTION_DATA_SIZE = int(os.getenv("CONNECTION_DATA_SIZE", "4096"))

# Declare the precision of the normalisation function
NORMALISATION_PRECISION = 3

# Declare names of the control models
CONTROL_AUTONOMOUS_NAME = "autonomous"
CONTROL_MANUAL_NAME = "manual"
CONTROL_MANAGER_NAME = "manager"

# Declare control's normal values
CONTROL_NORM_MAX = 1
CONTROL_NORM_IDLE = 0
CONTROL_NORM_MIN = -1

# Hardware values
THRUSTER_MAX = 1900
THRUSTER_IDLE = 1500
THRUSTER_MIN = 1100
GRIPPER_IDLE = 1500
CORD_IDLE = 1500

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
    "A_O": False,
    "A_I": False,
    "S_O": 0,
    "S_I": 0
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
    CONTROL_MANAGER_NAME + "-yaw": 0,
    CONTROL_MANAGER_NAME + "-pitch": 0,
    CONTROL_MANAGER_NAME + "-roll": 0,
    CONTROL_MANAGER_NAME + "-sway": 0,
    CONTROL_MANAGER_NAME + "-surge": 0,
    CONTROL_MANAGER_NAME + "-heave": 0,
    CONTROL_MANUAL_NAME + "-yaw": 0,
    CONTROL_MANUAL_NAME + "-pitch": 0,
    CONTROL_MANUAL_NAME + "-roll": 0,
    CONTROL_MANUAL_NAME + "-sway": 0,
    CONTROL_MANUAL_NAME + "-surge": 0,
    CONTROL_MANUAL_NAME + "-heave": 0,
    CONTROL_AUTONOMOUS_NAME + "-yaw": 0,
    CONTROL_AUTONOMOUS_NAME + "-pitch": 0,
    CONTROL_AUTONOMOUS_NAME + "-roll": 0,
    CONTROL_AUTONOMOUS_NAME + "-sway": 0,
    CONTROL_AUTONOMOUS_NAME + "-surge": 0,
    CONTROL_AUTONOMOUS_NAME + "-heave": 0,
    RK_CONTROL_DRIVING_MODE: DrivingMode.MANUAL.value
}
# Other, un-classified data
DATA_MISCELLANEOUS = {

}
