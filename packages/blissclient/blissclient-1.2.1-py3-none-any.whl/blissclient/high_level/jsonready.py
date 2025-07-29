# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Converter to be able to serialize some BLISS object with JSON.

It creates a language which can be deserialized in the client
side.
"""

import math
import numbers
import tblib
import typing

try:
    import pint
except ImportError:
    pint = None


def python_to_jsonready(content: typing.Any) -> typing.Any:
    if isinstance(content, list):
        return [python_to_jsonready(o) for o in content]
    if isinstance(content, tuple):
        return tuple(python_to_jsonready(o) for o in content)
    if isinstance(content, dict):
        return {k: python_to_jsonready(v) for k, v in content.items()}
    return obj_to_jsonready(content)


def obj_to_jsonready(obj: typing.Any) -> typing.Any:
    """
    Convert a single object into a valid json serializable
    """
    # To avoid cyclic import
    from .hardware import HardwareObject, HardwareRef

    if isinstance(obj, numbers.Real):
        if not math.isfinite(obj):
            # This are not supported by json
            if math.isnan(obj):
                return {"__type__": "nan"}
            if obj == -math.inf:
                return {"__type__": "neginf"}
            if obj == math.inf:
                return {"__type__": "posinf"}
            assert False, f"Unexpected {obj}"

    if pint is not None and isinstance(obj, pint.Quantity):
        return {
            "__type__": "quantity",
            "scalar": obj_to_jsonready(obj.magnitude),
            "unit": f"{obj.units:~}",
        }

    if isinstance(obj, BaseException):
        return {
            "__type__": "exception",
            "class": type(obj).__name__,
            "message": str(obj),
            "traceback": tblib.Traceback(obj.__traceback__).to_dict(),
        }

    if isinstance(obj, (HardwareObject, HardwareRef)):
        return {"__type__": "object", "name": obj.name}

    return obj


def python_from_jsonready(content: typing.Any) -> typing.Any:
    """
    Convert a single object into a valid json serializable
    """
    if isinstance(content, list):
        return [python_from_jsonready(o) for o in content]

    if not isinstance(content, dict):
        return content

    bliss_type = content.get("__type__")
    if bliss_type is None:
        return {k: python_from_jsonready(v) for k, v in content.items()}

    if bliss_type == "nan":
        return float("nan")

    if bliss_type == "neginf":
        return float("-inf")

    if bliss_type == "posinf":
        return float("inf")

    if bliss_type == "scan":
        # To avoid cyclic import
        from .scan import ScanRef

        scan_key = content.get("key")
        return ScanRef(scan_key)

    if bliss_type == "quantity" and pint is not None:
        return pint.Quantity(
            python_from_jsonready(content.get("scalar")),
            content.get("unit"),
        )

    if bliss_type == "object":
        # To avoid cyclic import
        from .hardware import HardwareRef

        name = content.get("name")
        return HardwareRef(name)

    if bliss_type == "exception":
        # Actually it's not a use case
        # No need to wast time on it
        raise RuntimeError("'exception' deserialisation is not allowed")

    return content
