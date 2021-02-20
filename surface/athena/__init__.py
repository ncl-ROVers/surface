"""
Central data storage and management functionalities.

Called "Athena" since the data manager holds all data and knows about state of the components, making it similar to the
goddess of wisdom.
"""
from .data_segment import DataSegment
from .data_manager import DataManager


__all__ = [
    "DataSegment",
    "DataManager",
]
