import os
from collections.abc import Callable

from .high_level.info import Info
from .high_level.session import Session
from .high_level.hardware import Hardware
from .high_level.events import Events
from .openapi.api_config import APIConfig


class BlissClient:
    """
    A BlissCLient.

    If an address is not specified the value have to be found in
    the environment variable `BLISSAPI_URL`.

    Arguments:
        base_path: A URL to a BLISS rest API, else None.
    """

    def __init__(self, base_path: str | None = None):
        if base_path is None:
            try:
                base_path = os.environ["BLISSAPI_URL"]
            except KeyError:
                raise RuntimeError("`BLISSAPI_URL` not defined in environemnt")
        api_config = APIConfig(base_path=base_path)
        self._api_config = api_config

        self._events = Events(api_config, self._socket_connected)
        self._hardware = Hardware(api_config, self._events)
        self._info = Info(api_config, self._events)
        self._session = Session(
            api_config,
            self._events,
            session_name=self.info.session,
            hardware=self._hardware,
        )
        self._hardware.set_session(self._session)

    def __str__(self):
        return f"BlissClient: {self.url}\n  Beamline: {self.beamline}\n  Session: {self.info.session}"

    def _socket_connected(self):
        self._hardware.socket_connected()
        self._session.socket_connected()

    def create_connect(self, async_client: bool = False, wait: bool = True):
        """Return a socketio creation function"""
        return self._events.create_connect(async_client=async_client, wait=wait)

    def register_callback(self, event_type: str, callback: Callable):
        """Register a callback for api connect / disconnect

        Valid `event_type`s are:
            - connect
            - connect_error
            - disconnect
        """
        self._session.register_callback(event_type, callback)

    @property
    def url(self) -> str:
        return self._api_config.base_path

    @property
    def info(self):
        return self._info.info

    @property
    def beamline(self):
        return self.info.beamline

    @property
    def session(self):
        return self._session

    @property
    def hardware(self):
        return self._hardware
