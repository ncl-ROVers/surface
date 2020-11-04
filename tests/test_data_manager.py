"""
Verify data manager's performance and correctness.
Due to all the data segments being functionally identical besides their name, all tests a custom data segment called
testing
Wont hit 100% coverage since that requires a RedisError (or packet exception)
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
    """
    Fixture that creates a DataManager and appends a 5th data segment for testing purposes
    Gets called by first test
    """
    r = Redis(host=REDIS_HOST, port=REDIS_PORT)
    d._segments.append(_DataSegment("testing", r, test_data))
    return d


def test_all(_setup_data_manager):
    """
    Quickly test that the data manager can be correctly created and the .all property works

    Calls the _setup_data_manager fixture, creating a DataManager for the rest of the tests
    This test must be executed first for the others to work
    """
    s = d._segments[5]
    assert s.all == test_data


def test_fetch_correctness():
    """
    Test that the fetch function works in DataManager and DataSegment

    Will fail if wrong data is returned
    """
    s = d._segments[5]
    returned_dictionary = s.fetch({"Alpha", "Iota", "Nu"})
    if returned_dictionary != {"Alpha": "Beta", "Iota": "Kappa", "Nu": "Xi"}:
        pytest.fail("Returned dictionary is not what expected for a normal use case", True)
    returned_dictionary = s.fetch({"Pepsi", "Gamma", "Window"})
    assert returned_dictionary == {"Gamma": "Delta"}


def test_update_correctness():
    """
    Test that the update function works in DataManager and DataSegment

    Fails if update doesnt correctly update certain values or if it fails to raise an exception when
    passed an incorrect key
    """
    s = d._segments[5]
    s.update({"Alpha": "NotBeta", "Gamma": "NotDelta"})
    if s["Alpha"] != "NotBeta" or s["Gamma"] != "NotDelta":
        pytest.fail("Update failed to correctly update the values", True)
    s.update({"Fail": 2020, "Alpha": 1998})
    with pytest.raises(DataManagerException):
        s["Fail"]


def test_getter_and_setters_correctness():
    """
    Test that values can be correctly obtained and changed using []

    Only fails if unexpected values are found instead. Note this can fail if Eta is changed in earlier tests
    """
    s = d._segments[5]
    assert s["Eta"] == "Theta"
    s["Eta"] = "NotTheta"
    assert s["Eta"] == "NotTheta"






