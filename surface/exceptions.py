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


class ComputerVisionException(SurfaceException):
    """
    Computer vision algorithms' errors.
    """


class ControlSystemException(SurfaceException):
    """
    Control model's errors and related.
    """
