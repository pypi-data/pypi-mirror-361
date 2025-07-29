from __future__ import annotations

from collections import deque
import datetime
import logging
import os
import time
from typing import Any, Callable, TypeVar

from .base import Base
from .scan import Scan
from ..openapi.services.CallApi_service import (
    _CallFunctionResourceV1_post_post,
    _CallFunctionStateResourceV1_get__call_id__get,
    _CallFunctionStateResourceV1_delete__call_id__delete,
)
from .hardware import Hardware
from ..openapi.models.CallFunction import CallFunction
from ..exceptions import BlissRESTNotFound, BlissRESTException
from .events import Events
from . import jsonready
from ..openapi.api_config import APIConfig

logger = logging.getLogger(__name__)

StdoutCallback = TypeVar("StdoutCallback", bound=Callable[[str], None])


class Session(Base):
    socketio_namespace = "/call"

    def __init__(
        self,
        api_config: APIConfig,
        events: Events,
        session_name: str,
        hardware: Hardware,
    ):
        self._on_stdout_callbacks: dict[str, StdoutCallback] = {}
        self._hardware = hardware
        self._data_store = None
        self._scans: deque[Scan] = deque([], 10)
        self._session_name = session_name
        super().__init__(api_config, events)

    def _socket_connected(self):
        self._on("stdout", self._on_stdout_event)

    def subscribe_stdout(self, call_id: str, callback: StdoutCallback):
        """Register a callback for stdout of a call

        The callback should have the following signature:
            `callback(message: str)`
        """
        if call_id not in self._on_stdout_callbacks:
            self._on_stdout_callbacks[call_id] = callback

    def unsubscribe_stdout(self, call_id: str):
        if call_id in self._on_stdout_callbacks:
            del self._on_stdout_callbacks[call_id]

    def _on_stdout_event(self, event_data: dict[str, Any]):
        call_id = event_data["call_id"]
        message = event_data["message"]
        logger.debug(f"stdout call_id:{call_id} message:{message}")
        if call_id in self._on_stdout_callbacks:
            self._on_stdout_callbacks[call_id](message)

    def _blissdata_address(self):
        address = os.environ.get("BLISSDATA_URL")
        if address is not None:
            return address

        base_path = self._api_config.base_path
        return base_path.replace("http://", "redis://").replace(":5000", ":6380")

    def load_scan(self, key: str, wrapped: bool = True):
        """Load a bliss scan from its blissdata redis key

        Args:
            wrapped: whether the scan is wrapped in a helper class"""
        try:
            if self._data_store is None:
                from blissdata.redis_engine.store import DataStore

                self._data_store = DataStore(self._blissdata_address())

            for scan in self._scans:
                if scan.key == key:
                    return scan

            scan = self._data_store.load_scan(key)
            if wrapped:
                scan = Scan(scan)
                self._scans.append(scan)
            return scan
        except Exception as e:
            print("Could not autoload bliss scan")
            print(e)

    def _potentially_load_scan_from_return(self, return_value: Any):
        if isinstance(return_value, dict):
            if "__type__" in return_value:
                if return_value["__type__"] == "scan" and "key" in return_value:
                    return self.load_scan(return_value["key"])

    def __str__(self):
        return f"Session: {self.name}"

    @property
    def name(self):
        """The current session name"""
        return self._session_name

    def call(
        self,
        function: str,
        *args,
        object_name: str = None,
        env_object_name: str = None,
        has_scan_factory: bool = False,
        emit_stdout: bool = False,
        in_terminal: bool = False,
        apply_jsonready_codec: bool = True,
        **kwargs,
    ):
        """Call a function in the session

        Kwargs:
            has_scan_factory: Assume the function returns a scan object
            env_object_name: Call a function on an object in the session
            object_name: Call a function on a registered object
            emit_stdout: Emit stdout over socketio to the /call namespace
            in_terminal: Execute the function in the terminal
            apply_jsonready_codec: If true the arguments and result arewrapped with jsonready codec

        Returns:
            call_id: uuid
        """
        if apply_jsonready_codec:
            args = jsonready.python_to_jsonready(args)
            kwargs = jsonready.python_to_jsonready(kwargs)

        response = _CallFunctionResourceV1_post_post(
            CallFunction(
                function=function,
                args=args,
                kwargs=kwargs,
                has_scan_factory=has_scan_factory,
                emit_stdout=emit_stdout,
                in_terminal=in_terminal,
                object=object_name,
                env_object=env_object_name,
            ),
            api_config_override=self._api_config,
        )

        future = CallFuture(
            self,
            response.call_id,
            function=function,
            args=args,
            kwargs={
                **kwargs,
                # "has_scan_factory": has_scan_factory,
                # "emit_stdout": emit_stdout,
                # "in_terminal": in_terminal,
                "object_name": object_name,
                "env_object_name": env_object_name,
            },
        )
        future.decode_jsonready = apply_jsonready_codec
        return future

    def state(self, call_id: str):
        """Get the state of a function call from its `call_id`"""
        state = _CallFunctionStateResourceV1_get__call_id__get(
            call_id=call_id,
            api_config_override=self._api_config,
        )

        scan_result = self._potentially_load_scan_from_return(state.return_value)
        if scan_result:
            state.return_value = scan_result
        return state

    def kill(self, call_id: str):
        """Kill a currently running function from its `call_id`"""
        _CallFunctionStateResourceV1_delete__call_id__delete(
            call_id=call_id, api_config_override=self._api_config
        )
        return True

    @property
    def scans(self):
        """Get the current list of scans retrieved from the session"""
        return self._scans

    @property
    def scan_saving(self):
        """Get the current `SCAN_SAVING` configuration"""
        scan_saving = self._hardware.get("SCAN_SAVING")
        return scan_saving


class CallFuture:
    """A future to interact with an async call to the REST API"""

    def __init__(
        self,
        session: Session,
        call_id: str,
        function: str,
        args: list[Any],
        kwargs: dict[str, Any],
    ):
        self._function = function
        self._args = args
        self._kwargs = kwargs
        self._started = time.time()
        self._call_id = call_id
        self._session = session
        self._result = None
        self._state = "running"
        self._progress = None
        self._exception = None
        self._stdout = ""
        self._stdout_callbacks: list[Callable] = []
        self.decode_jsonready = True

        self._session.subscribe_stdout(self._call_id, self._on_stdout)

    def subscribe_stdout(self, callback: Callable):
        """Subscribe to the stdout for this call"""
        if callback not in self._stdout_callbacks:
            self._stdout_callbacks.append(callback)

    def _on_stdout(self, message: str):
        self._stdout += f"{message}\n"
        for callback in self._stdout_callbacks:
            callback(message)

    @property
    def stdout(self):
        """The call stdout"""
        return self._stdout

    @property
    def call_id(self):
        """The `call_id` related to this future"""
        return self._call_id

    @property
    def state(self):
        """The state of the call"""
        self._update_state()
        return self._state

    @property
    def progress(self):
        """The progress (if implemented) of this call"""
        self._update_state()
        return self._progress

    def _test_progress(self):
        progress = self.progress
        if not progress:
            return False

        if "scan" not in progress:
            return False

        if not progress["scan"]:
            return False

        return True

    def wait_scan(self, monitor_interval: int = 5):
        """Wait for the scan `key` to be populated in the call `progress`

        Requires the call to be made with `has_scan_factory=True`
        """
        while not self._test_progress():
            time.sleep(monitor_interval)

        return self.progress

    def get(self, monitor_interval: int = 5):
        """Wait for the call to terminate and return the result"""
        while self._state == "running":
            self._update_state()
            time.sleep(monitor_interval)

        result = self._result
        if self.decode_jsonready:
            result = jsonready.python_from_jsonready(result)
        return result

    def kill(self):
        """Kill the currently running call"""
        return self._session.kill(self._call_id)

    def _update_state(self):
        try:
            state_response = self._session.state(self._call_id)
            self._progress = state_response.progress
            if state_response.state != "running":
                self._state = state_response.state
                self._result = state_response.return_value
                self._session.unsubscribe_stdout(self._call_id)
        except BlissRESTException as e:
            self._state = "failed"
            self._exception = e
            raise e
        except BlissRESTNotFound:
            pass

    def __str__(self):
        if self._exception:
            raise self._exception
        if self._state == "running":
            self._update_state()

        duration = datetime.timedelta(seconds=time.time() - self._started)
        time_string = f"{duration}" if self._state == "running" else f"took {duration}"
        return f"""CallFuture

    session:\t{self._session.name}
    function:\t`{self._function}`
    args:\t{self._args}, {self._kwargs}
    call_id:\t{self._call_id}
    state:\t{self._state} {time_string}"""
