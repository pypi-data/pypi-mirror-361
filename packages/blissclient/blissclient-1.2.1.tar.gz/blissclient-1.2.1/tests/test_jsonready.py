import math
import pint
from blissclient.high_level import jsonready
from blissclient.high_level.hardware import HardwareRef


def test_nan():
    result = jsonready.python_to_jsonready(float("nan"))
    assert result == {"__type__": "nan"}
    obj = jsonready.python_from_jsonready(result)
    assert math.isnan(obj)


def test_neginf():
    result = jsonready.python_to_jsonready(float("-inf"))
    assert result == {"__type__": "neginf"}
    obj = jsonready.python_from_jsonready(result)
    assert obj == -math.inf


def test_posinf():
    result = jsonready.python_to_jsonready(float("inf"))
    assert result == {"__type__": "posinf"}
    obj = jsonready.python_from_jsonready(result)
    assert obj == math.inf


def test_number():
    result = jsonready.python_to_jsonready(10.1)
    assert result == 10.1
    obj = jsonready.python_from_jsonready(result)
    assert obj == 10.1


def test_quantity():
    value = pint.Quantity(10.1, "mm")
    result = jsonready.python_to_jsonready(value)
    assert result == {
        "__type__": "quantity",
        "scalar": 10.1,
        "unit": "mm",
    }
    obj = jsonready.python_from_jsonready(result)
    assert obj == value


def test_neginf_quantity():
    value = pint.Quantity(float("+inf"), "mm")
    result = jsonready.python_to_jsonready(value)
    assert result == {
        "__type__": "quantity",
        "scalar": {"__type__": "posinf"},
        "unit": "mm",
    }
    obj = jsonready.python_from_jsonready(result)
    assert obj == value


def test_obj():
    robz = HardwareRef("robz")
    result = jsonready.python_to_jsonready(robz)
    assert result == {
        "__type__": "object",
        "name": "robz",
    }
    obj = jsonready.python_from_jsonready(result)
    assert obj.name == robz.name


def test_obj_in_dict():
    robz = HardwareRef("robz")
    data = {"robz": robz}
    result = jsonready.python_to_jsonready(data)
    assert result == {
        "robz": {
            "__type__": "object",
            "name": "robz",
        }
    }
    data2 = jsonready.python_from_jsonready(result)
    assert data2["robz"].name is robz.name


def test_obj_in_list():
    robz = HardwareRef("robz")
    data = [robz]
    result = jsonready.python_to_jsonready(data)
    assert result == [
        {
            "__type__": "object",
            "name": "robz",
        }
    ]
    data2 = jsonready.python_from_jsonready(result)
    assert data2[0].name == robz.name


def test_scan():
    result = {
        "__type__": "scan",
        "key": "foobar",
    }
    scan = jsonready.python_from_jsonready(result)
    assert scan.key == "foobar"
