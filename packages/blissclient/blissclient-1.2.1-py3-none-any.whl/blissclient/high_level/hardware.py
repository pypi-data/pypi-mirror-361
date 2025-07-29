from __future__ import annotations

import logging
import time
import weakref
from typing import Any, Callable, Literal

from ..openapi.api_config import APIConfig
from .base import Base
from .events import Events

from ..openapi.services.ObjectApi_service import (
    _HardwaresResourceV1_post_post,
    _HardwaresResourceV1_get_get,
    _HardwareResourceV1_get__string_name__get,
    _HardwareResourceV1_put__string_name__put,
)
from ..openapi.services.ObjectTypeApi_service import (
    _ObjectTypesResource_get_get,
    _ObjectTypeResource_get__string_id__get,
)
from ..openapi.models.RegisterHardwareSchema import RegisterHardwareSchema
from ..openapi.models.SetObjectProperty import SetObjectProperty
from ..openapi.models.ObjectSchema import ObjectSchema
from ..openapi.models.ObjectTypeSchema import ObjectTypeSchema
from . import jsonready

logger = logging.getLogger(__name__)


class HardwareRef:
    """A reference to an hardware name.

    Actually it's just a dummy object. which does not provide features.

    Attribute:
        name: Name of the BLISS object to reference
    """

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self):
        return self._name

    def to_jsonready(self) -> dict[str, str]:
        return {
            "__type__": "object",
            "name": self._name,
        }


class HardwareObject:
    """A `HardwareObject`

    Properties are mapped to python properties:
        print(omega.position)
        omega.velocity = 2000

    Functions can be directly called:
        omega.move(10)

    """

    _update_interval = 0.2

    def __init__(
        self,
        hardware: "Hardware",
        address: str,
        session,
        object_type: ObjectTypeSchema | None,
        initial_state: ObjectSchema | None = None,
        evented: bool = False,
    ):
        self.__hardware: weakref.ReferenceType[Hardware] = weakref.ref(hardware)
        self._last_status_time = 0
        self._state: ObjectSchema | None = initial_state
        self._address = address
        self._session = session
        self._evented = evented

        self._property_changed_callbacks: list[Callable] = []
        self._online_changed_callbacks: list[Callable] = []
        self._locked_changed_callbacks: list[Callable] = []

        self._get_status()

        self._object_type: ObjectTypeSchema
        if object_type is not None:
            self._object_type = object_type
        else:
            api_config = self._api_config
            self._object_type = _ObjectTypeResource_get__string_id__get(
                self._state.type, api_config_override=api_config
            )

        for callable in self._object_type.callables:
            setattr(self, callable, self._make_callable(callable))

    @property
    def _api_config(self) -> APIConfig:
        hardware = self._hardware
        if hardware is None:
            raise RuntimeError("Hardware service was already released")
        return hardware._api_config

    @property
    def _hardware(self) -> "Hardware" | None:
        """Return the hardware service which have created this object"""
        return self.__hardware()

    def subscribe(
        self, event_type: Literal["property", "online", "locked"], callback: Callable
    ):
        """Subscribe to an event on this object

        This can subscribe to object
            - property changes (position, velocity, etc)
            - online status changes
            - lock changes
        """
        if event_type == "property":
            if callback not in self._property_changed_callbacks:
                self._property_changed_callbacks.append(callback)
        if event_type == "online":
            if callback not in self._online_changed_callbacks:
                self._online_changed_callbacks.append(callback)
        if event_type == "locked":
            if callback not in self._locked_changed_callbacks:
                self._locked_changed_callbacks.append(callback)

    def set_evented(self, evented: bool):
        self._evented = evented

    def __dir__(self):
        return super().__dir__() + list(self._state.properties.keys())

    def __str__(self):
        properties = "".join(
            [
                f"  {property}:\t{value}\n"
                for property, value in self._state.properties.items()
            ]
        )
        callables = ", ".join(self._object_type.callables)

        errors = ""
        if self.errors:
            errors = f"! Errors: \n  {self.errors}"

        locked = "None"
        if self._state.locked:
            locked = self._state.locked.reason

        return f"""Address: {self._address} ({self.type})
{errors}
Online: {self._state.online}
Lock State: {locked}
Tags: {self._state.user_tags}

Properties:
{properties}

Callables:
  {callables}

"""

    @property
    def name(self):
        return self._address

    @property
    def type(self):
        return self._state.type

    @property
    def errors(self):
        return self._state.errors

    @property
    def properties(self):
        return self._state.properties

    def _convert_ref_as_object(self, ref: str):
        """Convert a object ref value into an object."""
        if not ref.startswith("hardware:"):
            logger.warning("ObjectRef expected. Found '%s'", ref)
            return None

        name = ref[9:]
        if name == "":
            return None

        hardware = self._hardware
        if hardware is None:
            raise RuntimeError("Hardware service was released")
        return hardware.get(name)

    def _is_object_ref(self, prop_name: str):
        prop_desc = self._object_type.properties.get(prop_name, {})
        # FIXME: blissTpe was a typo in the protocol
        blissType = prop_desc.get("blissTpe") or prop_desc.get("blissType")
        # FIXME: Should be renamed "object_ref" in the protocol
        return blissType == "hardware_ref"

    def __getattr__(self, item: str):
        state = object.__getattribute__(self, "_state")
        if state:
            get_status = object.__getattribute__(self, "_get_status")
            get_status()
            state = object.__getattribute__(self, "_state")
            if item in state.properties:
                value = state.properties[item]
                if self._is_object_ref(item):
                    # Transparent support of object ref
                    if isinstance(value, list):
                        return (self._convert_ref_as_object(v) for v in value)
                    else:
                        return self._convert_ref_as_object(value)
                return value

        return super().__getattribute__(item)

    def __setattr__(self, item: str, value: Any):
        if hasattr(self, "_state"):
            if self._state:
                if item in self._state.properties:
                    self._set(item, value)

        return super().__setattr__(item, value)

    def _make_callable(self, function: str):
        def call_function(*args, **kwargs):
            args = jsonready.python_to_jsonready(args)
            kwargs = jsonready.python_to_jsonready(kwargs)
            result = self._call(function, *args, **kwargs)
            result = jsonready.python_from_jsonready(result)
            return result

        return call_function

    def update_state(self, log: bool = True):
        """Request update of state"""
        if log:
            logger.info(f"Requesting state for {self.name}")
        self._state = _HardwareResourceV1_get__string_name__get(
            name=self._address, api_config_override=self._api_config
        )

    def _get_status(self):
        if self._evented:
            return

        now = time.time()
        if now - self._last_status_time > self._update_interval:
            self.update_state(log=False)
            self._last_status_time = now
        else:
            logger.debug(
                f"Requesting update for {self.name}, ignoring last update {now - self._last_status_time}s ago"
            )

    def _call(self, function: str, *args, **kwargs):
        return self._session.call(function, object_name=self.name, *args, **kwargs)

    def _set(self, property: str, value: Any):
        if self._is_object_ref(property):
            if value is not None and not isinstance(
                value, (HardwareObject, HardwareRef)
            ):
                # TODO: We could also support pure reference which are not
                #       linked to a registred object
                raise ValueError(
                    f"Expected an HardwareObject, HardwareRef or None. Found {value}"
                )
            if value is None:
                value = "hardware:"
            else:
                value = f"hardware:{value.name}"

        return _HardwareResourceV1_put__string_name__put(
            name=self._address,
            data=SetObjectProperty(property=property, value=value),
            api_config_override=self._api_config,
        )

    def _update_property(self, data: dict[str, Any]):
        logger.debug(f"_update_property `{self.name}` `{data}`")
        for key, value in data.items():
            if key in self._state.properties.keys():
                self._state.properties[key] = value

        for callback in self._property_changed_callbacks:
            callback(data)

    def _update_online(self, online: bool):
        logger.debug(f"_update_online `{self.name}` {online}")
        self._state.online = online
        for callback in self._online_changed_callbacks:
            callback(online)

    def _update_locked(self, reason: dict[str, Any]):
        logger.debug(f"_update_locked {self.name} {reason}")
        self._state.locked = reason
        for callback in self._locked_changed_callbacks:
            callback(reason)


class Hardware(Base):
    socketio_namespace = "/object"

    def __init__(self, api_config: APIConfig, events: Events):
        self._session = None
        self._objects: dict[str, HardwareObject] = {}
        self._cached_initial_statuses: dict[str, ObjectSchema] = {}

        self._evented = False
        super().__init__(api_config, events)

        self._object_types = _ObjectTypesResource_get_get(
            api_config_override=self._api_config
        )

    @property
    def types(self) -> dict[str, ObjectTypeSchema]:
        """Return the known types"""
        return {t.type: t for t in self._object_types.results}

    def get_type(self, name: str) -> ObjectTypeSchema | None:
        """Get a type, else None if it does not exists."""
        for t in self._object_types.results:
            if t.type == name:
                return t
        return None

    def set_session(self, session):
        self._session = session

    def _socket_connected(self):
        self._on("change", self._on_change_event)
        self._on("online", self._on_online_event)
        self._on("locked", self._on_locked_event)
        self._evented = True
        for obj in self._objects.values():
            obj.set_evented(True)

    def _on_change_event(self, event_data: dict[str, Any]):
        object_id = event_data.get("id")
        data = event_data.get("data")
        if isinstance(data, dict):
            if object_id in self._objects:
                self._objects[object_id]._update_property(data)

    def _on_online_event(self, event_data: dict[str, Any]):
        object_id = event_data.get("id")
        if object_id in self._objects:
            self._objects[object_id]._update_online(event_data.get("state"))

    def _on_locked_event(self, event_data: dict[str, Any]):
        object_id = event_data.get("id")
        logger.debug(f"_on_locked_event {event_data}")
        if object_id in self._objects:
            self._objects[object_id]._update_locked(event_data.get("state"))

    def __str__(self):
        objects = "".join([f"  {address}\n" for address in self.available])
        return f"Hardware:\n{objects}"

    def _get_initial_status(self):
        response = _HardwaresResourceV1_get_get(api_config_override=self._api_config)
        self._cached_initial_statuses = {item.name: item for item in response.results}

    @property
    def available(self):
        """List the currently available `HardwareObjects`"""
        return list(self._cached_initial_statuses.keys())

    def register(self, *addresses: str):
        """Register a `HardwareObject` with the bliss REST API"""
        response = _HardwaresResourceV1_post_post(
            data=RegisterHardwareSchema(names=list(addresses)),
            api_config_override=self._api_config,
        )
        self._get_initial_status()
        return response

    def reregister(self):
        """Re-register objects in case of disconnect / API restart"""
        self.register(*list(self._objects.keys()))

    def get(self, address: str) -> HardwareObject:
        """Get a hardware object from its beacon `address`"""
        if address in self._objects:
            return self._objects[address]

        if address not in self.available:
            logger.info(
                f"Object `{address}` not yet available, trying to register it..."
            )
            self.register(address)

        initial_state = self._cached_initial_statuses.get(address)
        object_type = self.get_type(initial_state.type)

        obj = HardwareObject(
            hardware=self,
            address=address,
            session=self._session,
            object_type=object_type,
            initial_state=initial_state,
            evented=self._evented,
        )
        self._objects[address] = obj
        return obj
