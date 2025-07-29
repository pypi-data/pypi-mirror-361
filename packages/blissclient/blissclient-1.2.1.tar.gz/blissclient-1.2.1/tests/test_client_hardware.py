import pytest
from blissclient import HardwareObject, BlissClient, Hardware
from blissclient.exceptions import (
    BlissRESTCantRegister,
    BlissRESTValidationError,
    BlissRESTNotFound,
)
from pydantic import ValidationError


def test_client_hardware_available(hardware: Hardware):
    assert isinstance(hardware.available, list)


def test_client_hardware_register(hardware: Hardware):
    response = hardware.register("robx")
    assert response.names == ["robx"]


def test_client_hardware(robx: HardwareObject):
    assert robx.name == "robx"
    future = robx.move(5)
    future.get()

    future = robx.move(10)
    future.get()
    assert robx.position == 10

    robx.velocity = 5
    robx.velocity = 5000
    assert robx.velocity == 5000


def test_client_hardware_call_kill(robx: HardwareObject):
    old_velocity = robx.velocity
    robx.velocity = 1
    future = robx.move(1000)
    future.kill()
    robx.velocity = old_velocity


def test_client_hardware_422(robx: HardwareObject):
    with pytest.raises(BlissRESTValidationError):
        robx.move("string")


def test_client_hardware_invalid_type(robx: HardwareObject):
    with pytest.raises(ValidationError):
        robx._call(123, 123)


def test_client_hardware_404(robx: HardwareObject):
    with pytest.raises(BlissRESTNotFound):
        robx._call("moo", 123)


def test_client_hardware_missing(blissclient: BlissClient):
    with pytest.raises(BlissRESTCantRegister):
        blissclient.hardware.get("missing")


def test_client_hardware_types(blissclient: BlissClient):
    assert blissclient.hardware.types.get("motor")
    assert blissclient.hardware.get_type("motor").type == "motor"
