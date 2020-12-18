"""
Constants and other static values.
"""
import os
import dotenv
from .enums import ConnectionStatus

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

# Declare connection address - use .env file to override the defaults
CONNECTION_IP = os.getenv("CONNECTION_IP", "localhost")
CONNECTION_PORT = int(os.getenv("CONNECTION_PORT", "50000"))

# Declare connection keys
RK_CONNECTION_SURFACE_PI = "surface-pi"

# Declare data dictionaries (that will be stored in cache) with their defaults (RK stands for Redis Key)
# Connection statuses between various components of the vehicle
DATA_CONNECTIONS = {
    RK_CONNECTION_SURFACE_PI: ConnectionStatus.DISCONNECTED
}
# Data received from Raspberry Pi
DATA_RECEIVED = {

}
# Data that will be sent to Raspberry Pi
DATA_TRANSMISSION = {

}
# Autonomous, manual, and assisted control system data
DATA_CONTROL = {

}
# Other, un-classified data
DATA_MISCELLANEOUS = {

}
