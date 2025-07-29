from __future__ import annotations

import logging
from typing import Callable

from ..openapi.api_config import APIConfig
from .events import Events

logger = logging.getLogger(__name__)


class Base:
    socketio_namespace: str | None = None

    def __init__(self, api_config: APIConfig, events: Events):
        self._api_config = api_config
        self._on_connect_callbacks: list[Callable] = []
        self._on_connect_error_callbacks: list[Callable] = []
        self._on_disconnect_callbacks: list[Callable] = []
        self._events = events

    def register_callback(self, event_type: str, callback: Callable):
        if event_type == "connect":
            if callback not in self._on_connect_callbacks:
                self._on_connect_callbacks.append(callback)
        elif event_type == "connect_error":
            if callback not in self._on_connect_error_callbacks:
                self._on_connect_error_callbacks.append(callback)
        elif event_type == "disconnect":
            if callback not in self._on_disconnect_callbacks:
                self._on_disconnect_callbacks.append(callback)

    def _on(self, event: str, callback: Callable):
        """Convience wrapper to register socketio event callback"""
        return self._events.socketio.on(
            event=event, handler=callback, namespace=self.socketio_namespace
        )

    def socket_connected(self):
        self._on("connect", self._on_connect)
        self._on("connect_error", self._on_connect_error)
        self._on("disconnect", self._on_disconnect)

        self._socket_connected()

    def _on_connect(self):
        logger.info(f"blissclient: Connected to namespace: {self.socketio_namespace}")
        for callback in self._on_connect_callbacks:
            callback()

    def _on_connect_error(self, err):
        logger.info(
            f"blissclient: SocketIO could not connect to `{self.socketio_namespace}`: {str(err)}"
        )
        for callback in self._on_connect_error_callbacks:
            callback(err)

    def _on_disconnect(self):
        logger.info(
            f"blissclient: SocketIO disconnected from `{self.socketio_namespace}`"
        )
        for callback in self._on_disconnect_callbacks:
            callback()
