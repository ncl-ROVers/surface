"""
Networking constants.
"""
import os

# Declare connection information - use .env file to override the defaults
CONNECTION_IP = os.getenv("CONNECTION_IP", "localhost")
CONNECTION_PORT = int(os.getenv("CONNECTION_PORT", "50000"))
CONNECTION_DATA_SIZE = int(os.getenv("CONNECTION_DATA_SIZE", "4096"))
