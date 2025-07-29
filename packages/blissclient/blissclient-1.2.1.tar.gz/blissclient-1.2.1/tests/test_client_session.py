import time
import pytest

from blissclient import Session, get_object
from blissclient.exceptions import (
    BlissRESTException,
    BlissRESTNotFound,
)


def test_client_session_name(test_session: Session):
    assert "demo_session" == test_session.name


def test_client_session_scan_saving(test_session: Session):
    assert test_session.scan_saving.proposal_name
    new_collection = "test_collection"
    test_session.scan_saving.collection_name = new_collection
    assert test_session.scan_saving.collection_name == new_collection
    test_session.scan_saving.create_root_path()


def test_client_session_function_non_existant(test_session: Session):
    with pytest.raises(BlissRESTNotFound):
        test_session.call("test")


def test_client_session_call_scan(test_session: Session):
    future = test_session.call(
        "ascan", get_object("robx"), 0, 5, 5, 0.2, get_object("diode1")
    )
    scan = future.get()
    assert scan.key


def test_client_session_call_scan_invalid_args(test_session: Session):
    future = test_session.call("ascan", 1, 0, 5, 5, 0.2, get_object("diode1"))
    with pytest.raises(
        BlissRESTException,
        match="Intended Usage: ascan\\(motor, start, stop, intervals, count_time, counter_args\\)",
    ):
        future.get()


def test_client_session_call_kill(test_session: Session):
    future = test_session.call(
        "ascan", get_object("robx"), 0, 10, 10, 1, get_object("diode1")
    )
    time.sleep(1)
    future.kill()
    # allow small sync time
    time.sleep(2)

    assert future.state == "killed"
