"""
Verify data manager's performance and correctness.
Due to all the data segments being functionally identical besides their name, all tests use the
miscellaneous data segment
"""

from redis import Redis, RedisError
from surface.constants import REDIS_HOST, REDIS_PORT
import pytest

from surface.data_manager import DataManager, _DataSegment
from surface.exceptions import DataManagerException

test_data = {
    "Alpha": "Beta",
    "Gamma": "Delta",
    "Epsilon": "Zeta",
    "Eta": "Theta",
    "Iota": "Kappa",
    "Lambda": "Mu",
    "Nu": "Xi",
}

d = DataManager()


@pytest.fixture
def _setup_data_manager():
    r = Redis(host=REDIS_HOST, port=REDIS_PORT)
    d._segments.append(_DataSegment("testing", r, test_data))
    return d


def test_all(_setup_data_manager):
    s = d._segments[5]
    assert s.all == test_data


def test_fetch_correctness():
    s = d._segments[5]
    returned_dictionary = s.fetch({"Alpha", "Iota", "Nu"})
    if returned_dictionary != {"Alpha": "Beta", "Iota": "Kappa", "Nu": "Xi"}:
        pytest.fail("Returned dictionary is not what expected for a normal use case", True)
    returned_dictionary = s.fetch({"Pepsi", "Gamma", "Window"})
    assert returned_dictionary == {"Gamma": "Delta"}


def test_update_correctness():
    s = d._segments[5]
    s.update({"Alpha": "NotBeta", "Gamma": "NotDelta"})
    if s["Alpha"] != "NotBeta" or s["Gamma"] != "NotDelta":
        pytest.fail("Update failed to correctly update the values", True)
    s.update({"Fail": 873})
    with pytest.raises(DataManagerException):
        s["Fail"]






