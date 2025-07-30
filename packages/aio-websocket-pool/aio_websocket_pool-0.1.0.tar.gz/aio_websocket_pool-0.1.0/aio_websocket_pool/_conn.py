from __future__ import annotations

import asyncio as aio
import contextlib
import logging
import time
import types
import typing as t
import uuid

import websockets.asyncio.client as ws
import websockets.exceptions as ws_exc
import websockets.protocol as ws_protocol

from . import WebsocketError

logger = logging.getLogger(__name__)


class ConnectionBusyError(WebsocketError):
    pass


class ConnectionUnavailableError(WebsocketError):
    pass


class ConnectionClosedError(WebsocketError):
    pass


class ConnectionDrainTimeoutError(WebsocketError):
    pass


# Type alias for drain condition callback
DrainConditionCallback = t.Callable[[t.Union[str, bytes]], bool]


class WebsocketConnection(t.Hashable, t.AsyncContextManager):

    def __init__(
        self,
        *,
        uri: str,
        headers: t.Dict[str, str] | None = None,
        idle_timeout: float = 30.0,
        check_server_data_on_release: bool = False,
        drain_timeout: float = 5.0,
        drain_condition: DrainConditionCallback | None = None,
        **kwargs: t.Any,
    ):
        self.uri = uri
        self.headers = headers
        self.idle_timeout = idle_timeout
        self.check_server_data_on_release = check_server_data_on_release
        self.drain_timeout = drain_timeout
        self.drain_condition = drain_condition or self._default_drain_condition
        self._params = kwargs

        self.websocket: ws.ClientConnection | None = None
        self._is_busy = False
        self._is_draining = False
        self._last_activity = time.time()
        self._monitor_task: aio.Task | None = None
        self._closed = False
        self._lock = aio.Lock()
        self._connection_id = uuid.uuid4().hex  # for hashing

    @staticmethod
    def _default_drain_condition(message: str | bytes) -> bool:
        """Default condition to determine if incoming data should be drained.

        Args:
            message: The incoming message from the server

        Returns:
            True if the message should be drained (considered as server data)
        """
        # By default, consider any non-empty message as server data
        return len(message) > 0

    @property
    def is_busy(self) -> bool:
        return self._is_busy

    @property
    def is_draining(self) -> bool:
        return self._is_draining

    @property
    def is_connected(self) -> bool:
        return (
                self.websocket is not None
                and not self._closed
                and self.websocket.state == ws_protocol.OPEN
        )

    @property
    def last_activity(self) -> float:
        return self._last_activity

    def _update_activity(self) -> None:
        self._last_activity = time.time()

    async def _monitor_idle(self) -> None:
        try:
            while not self._closed:
                should_close = False
                async with self._lock:
                    if (
                            self.is_connected
                            and not self.is_busy
                            and not self.is_draining
                            and (time.time() - self._last_activity) > self.idle_timeout
                    ):
                        should_close = True

                if should_close:
                    logger.debug(f"Closing idle connection to {self.uri}")
                    await self.close()
                    break
                await aio.sleep(1)
        except aio.CancelledError:
            pass

    async def connect(self) -> None:
        if self.is_connected:
            return

        if self._closed:
            raise ConnectionUnavailableError("Connection has been closed")

        if self._monitor_task is not None and self._monitor_task.done():
            try:
                await self._monitor_task
            finally:
                self._monitor_task = None

        try:
            self.websocket = await ws.connect(
                self.uri, additional_headers=self.headers, **self._params
            )
            self._update_activity()

            # Start monitor task if not already running
            if self._monitor_task is None or self._monitor_task.done():
                self._monitor_task = aio.create_task(self._monitor_idle())

            logger.debug(f"Connected to {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to {self.uri}: {e}")
            raise ConnectionUnavailableError(f"Failed to connect: {e}") from e

    async def close(self) -> None:
        async with self._lock:
            if self._closed:
                return

            self._closed = True

            # Cancel monitor task
            if self._monitor_task is not None:
                if not self._monitor_task.done():
                    self._monitor_task.cancel()

                try:
                    await self._monitor_task
                except aio.CancelledError:
                    logger.debug(f"Monitor task for {self.uri} cancelled")
                finally:
                    self._monitor_task = None

            # Close websocket
            if self.websocket is not None:
                try:
                    await self.websocket.close()
                finally:
                    self.websocket = None

            self._is_busy = False
            self._is_draining = False
            logger.debug(f"Closed connection to {self.uri}")

    async def acquire(self) -> None:
        async with self._lock:
            if self._closed:
                raise ConnectionUnavailableError("Connection has been closed")
            if self._is_busy:
                raise ConnectionBusyError("Connection is already busy")
            if self._is_draining:
                raise ConnectionBusyError("Connection is currently draining")

            try:
                await self.connect()
                self._is_busy = True
                self._update_activity()
            except Exception as e:
                logger.error(f"Failed to acquire connection to {self.uri}: {e}")
                raise ConnectionUnavailableError(f"Failed to acquire connection: {e}") from e

    async def release(self) -> None:
        async with self._lock:
            if not self._is_busy:
                return

            self._is_busy = False
            self._update_activity()

    async def ping(self) -> None:
        if not (
                self.websocket is not None
                and not self._closed
                and self.websocket.state == ws_protocol.OPEN
        ):
            raise ConnectionUnavailableError("Websocket is not connected")
        connection_closed = False
        connection_closed_error = None
        async with self._lock:
            if not self.is_connected:
                raise ConnectionUnavailableError("Websocket is not connected")
            try:
                await self.websocket.ping()
                self._update_activity()
            except ws_exc.ConnectionClosed as e:
                logger.error(f"Connection closed during ping: {e}")
                connection_closed = True
                connection_closed_error = e

        if connection_closed:
            await self.close()
            raise ConnectionClosedError(
                f"Connection closed during ping: {connection_closed_error}"
            ) from connection_closed_error

    @contextlib.asynccontextmanager
    async def session(self) -> t.AsyncGenerator[WebsocketConnection, None]:
        await self.acquire()
        try:
            yield self
        finally:
            await self.release()

    async def send(self, message: str | bytes) -> None:
        if not self.is_busy:
            raise ConnectionBusyError("Connection must be acquired before sending messages")
        if not (
                self.websocket is not None
                and not self._closed
                and self.websocket.state == ws_protocol.OPEN
        ):
            raise ConnectionUnavailableError("Websocket is not connected")
        try:
            await self.websocket.send(message)
            self._update_activity()
        except ws_exc.ConnectionClosed as e:
            await self.close()
            logger.error(f"Connection closed while sending message: {e}")
            raise ConnectionClosedError(f"Connection closed while sending message: {e}") from e

    async def recv(self) -> str | bytes:
        if not self._is_busy:
            raise ConnectionBusyError("Connection must be acquired before receiving messages")
        if not (
                self.websocket is not None
                and not self._closed
                and self.websocket.state == ws_protocol.OPEN
        ):
            raise ConnectionUnavailableError("Websocket is not connected")
        try:
            message = await self.websocket.recv()
            self._update_activity()
            return message
        except ws_exc.ConnectionClosed as e:
            await self.close()
            logger.error(f"Connection closed while receiving message: {e}")
            raise ConnectionClosedError(f"Connection closed while receiving message: {e}") from e

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"connection_id={self._connection_id}, "
            f"uri={self.uri}, "
            f"busy={self._is_busy}, "
            f"draining={self._is_draining}, "
            f"connected={self.is_connected}, "
            f"closed={self._closed})"
        )

    def __str__(self) -> str:
        return f"WebsocketConnection({self._connection_id})"

    def __hash__(self) -> int:
        return hash(self._connection_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WebsocketConnection):
            return NotImplemented
        return self._connection_id == other._connection_id

    async def __aenter__(self) -> t.Self:
        await self.connect()
        await self.acquire()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None, /
    ) -> t.Literal[False]:
        await self.close()
        return False


__all__ = [
    "ConnectionClosedError",
    "ConnectionBusyError",
    "ConnectionUnavailableError",
    "ConnectionDrainTimeoutError",
    "WebsocketError",
    "WebsocketConnection",
    "DrainConditionCallback",
]
