"""
Hierarchy of all exceptions within the application.
"""


class SurfaceException(Exception):
    """
    Base exception for all errors in this application.
    """


class DataManagerException(SurfaceException):
    """
    DataManager and DataSegment errors.
    """


class NetworkingException(SurfaceException):
    """
    Connection and video streaming errors.
    """
