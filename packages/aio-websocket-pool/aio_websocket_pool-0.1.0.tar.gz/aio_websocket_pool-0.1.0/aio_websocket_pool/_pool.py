from __future__ import annotations

import asyncio as aio
import collections
import contextlib
import logging
import time
import types
import typing as t
import uuid

import tenacity

from . import WebsocketError
from ._conn import (
    ConnectionBusyError,
    ConnectionClosedError,
    ConnectionUnavailableError,
    DrainConditionCallback,
    WebsocketConnection,
)

logger = logging.getLogger(__name__)


class ConnectionPoolExhaustedError(WebsocketError):
    pass


class ConnectionPoolUnavailableError(WebsocketError):
    pass


class PendingConnection:
    """Represents a connection that is being drained before being returned to
    the pool."""

    def __init__(
        self,
        connection: WebsocketConnection,
        drain_timeout: float,
        drain_condition: DrainConditionCallback,
    ):
        self.connection = connection
        self.drain_timeout = drain_timeout
        self.drain_condition = drain_condition
        self.created_at = time.time()
        self.drain_task: aio.Task | None = None
        self.pending_id = uuid.uuid4().hex

    def __repr__(self) -> str:
        return f"PendingConnection({self.pending_id}, {self.connection})"


class WebsocketConnectionPool(t.AsyncContextManager):
    """An asynchronous WebSocket connection pool for managing reusable
    WebSocket connections.

    This class provides efficient and fault-tolerant management of a pool of
    WebSocket connections to a specified URI. It supports connection reuse,
    automatic cleanup of idle or disconnected connections, retry mechanisms,
    optional warm-up on startup, and server data detection during connection
    release.

    Key Features:
        - Connection reuse.
        - Connection acquisition with automatic exponential backoff retries.
        - Optional warm-up of initial connections.
        - Background cleanup of idle or disconnected connections.
        - Asynchronous server data draining to prevent data loss.
        - Supports context management for automatic connection release.

    Attributes:
        uri (str): The WebSocket URI to connect to.
        headers (dict): Optional headers sent with each connection.
        _idle_timeout (float):
            Time in seconds before idle connections are closed.
        _max_connections (int):
            Maximum total number of connections in the pool.
        _max_retries (int):
            Number of retry attempts on connection acquisition failures.
        _cleanup_interval (float): Time in seconds between idle cleanup runs.
        _connection_timeout (float): Timeout for establishing new connections.
        _warmup_connections (int):
            Number of connections to establish on startup.
        _check_server_data_on_release (bool):
            Whether to check for server data during release.
        _drain_timeout (float):
            Timeout for draining server data during release.
        _drain_condition (DrainConditionCallback):
            Function to determine what constitutes server data.
        _drain_quiet_period (float):
            Time to wait without receiving data before considering connection
            clean.
    """

    def __init__(
        self,
        *,
        uri: str,
        headers: t.Dict[str, str] | None = None,
        idle_timeout: float = 60.0,
        max_connections: int = 50,
        max_retries: int = 3,
        cleanup_interval: float = 5.0,
        connection_timeout: float = 10.0,
        warmup_connections: int = 0,
        check_server_data_on_release: bool = False,
        drain_timeout: float = 10.0,
        drain_quiet_period: float = 2.0,
        drain_condition: DrainConditionCallback | None = None,
        **kwargs: t.Any,
    ):
        """Initialize a WebSocket connection pool.

        Args:
            uri: The WebSocket URI to connect to.
            headers: Optional HTTP headers to include in connection requests.
            idle_timeout: Maximum time in seconds a connection can remain idle
                before being closed. Defaults to 60.0.
            max_connections: Maximum number of concurrent connections allowed
                in the pool. Defaults to 50.
            max_retries: Maximum number of retry attempts when acquiring a
                connection fails. Defaults to 3.
            cleanup_interval: Interval in seconds between cleanup operations
                for idle connections. Defaults to 5.0.
            connection_timeout: Timeout in seconds for establishing new
                connections. Defaults to 10.0.
            warmup_connections: Number of connections to create during pool
                initialization. Defaults to 0.
            check_server_data_on_release: Whether to check for server data
                during connection release. Defaults to False.
            drain_timeout: Maximum time in seconds to drain server data
                during release. Defaults to 10.0.
            drain_quiet_period: Time in seconds to wait without receiving data
                before considering connection clean. Defaults to 2.0.
            drain_condition: Function to determine what constitutes server data
                that should be drained. Defaults to None (uses default
                condition).
            **kwargs: Additional parameters to pass to WebsocketConnection.
        """
        self.uri = uri
        self.headers = headers or {}
        self._idle_timeout = idle_timeout
        self._max_connections = max_connections
        self._max_retries = max_retries
        self._cleanup_interval = cleanup_interval
        self._connection_timeout = connection_timeout
        self._warmup_connections = warmup_connections
        self._check_server_data_on_release = check_server_data_on_release
        self._drain_timeout = drain_timeout
        self._drain_quiet_period = drain_quiet_period
        self._drain_condition = drain_condition or self._default_drain_condition
        self._params = kwargs

        self._available: t.Deque[WebsocketConnection] = collections.deque()
        self._busy: t.Set[WebsocketConnection] = set()
        self._pending: t.Dict[str, PendingConnection] = {}
        self._total = 0
        self._lock = aio.Lock()
        self._closed = False
        self._cleanup_task: aio.Task | None = None
        self._started = False

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
    def is_closed(self) -> bool:
        """Check if the connection pool is closed.

        Returns:
            True if the pool is closed, False otherwise.
        """
        return self._closed

    @property
    def is_started(self) -> bool:
        """Check if the connection pool has been started.

        Returns:
            True if the pool has been started, False otherwise.
        """
        return self._started

    @property
    def total_connections(self) -> int:
        """Get the total number of connections in the pool.

        Returns:
            The total number of connections (available, busy, and pending).
        """
        return self._total

    @property
    def available_connections(self) -> int:
        """Get the number of available connections.

        Returns:
            The number of connections available for use.
        """
        return len(self._available)

    @property
    def busy_connections(self) -> int:
        """Get the number of busy connections.

        Returns:
            The number of connections currently in use.
        """
        return len(self._busy)

    @property
    def pending_connections(self) -> int:
        """Get the number of pending connections.

        Returns:
            The number of connections being drained.
        """
        return len(self._pending)

    def _create_connection(self) -> WebsocketConnection:
        """Create a new WebsocketConnection with pool configuration."""
        return WebsocketConnection(
            uri=self.uri,
            headers=self.headers,
            idle_timeout=self._idle_timeout,
            check_server_data_on_release=self._check_server_data_on_release,
            drain_timeout=self._drain_timeout,
            drain_condition=self._drain_condition,
            **self._params,
        )

    async def start(self) -> None:
        """Start the connection pool.

        Initializes the pool, starts the cleanup task, and optionally
        creates warmup connections if configured.
        """
        if self._started or self._closed:
            return

        self._started = True
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = aio.create_task(self._cleanup_loop())

        # Warmup connections if specified
        if self._warmup_connections > 0:
            await self._warmup_pool()

        logger.info(f"Started WebSocket connection pool for {self.uri}")

    async def _warmup_pool(self) -> None:
        warmup_count = min(self._warmup_connections, self._max_connections)

        for _ in range(warmup_count):
            try:
                connection = self._create_connection()
                await aio.wait_for(connection.connect(), timeout=self._connection_timeout)
                self._available.append(connection)
                self._total += 1

                logger.debug(f"Warmed up connection: {connection}")

            except Exception as e:
                logger.warning(f"Failed to warm up connection: {e}")
                break

        logger.info(f"Warmed up {len(self._available)} connections")

    async def acquire(self) -> WebsocketConnection:
        """Acquire a connection from the pool.

        Attempts to reuse an existing available connection, or creates a new
        one if none are available and the pool limit hasn't been reached.
        Includes automatic retry logic for transient failures.

        Returns:
            An acquired WebsocketConnection ready for use.

        Raises:
            ConnectionPoolUnavailableError: If the pool is closed.
            ConnectionPoolExhaustedError:
                If maximum connections limit is reached.
            ConnectionUnavailableError:
                If connection acquisition fails after retries.
        """
        if not self._started:
            await self.start()

        retry = tenacity.retry(
            stop=tenacity.stop_after_attempt(self._max_retries),
            wait=tenacity.wait_exponential(multiplier=1, max=10),
            retry=tenacity.retry_if_exception_type(
                (ConnectionUnavailableError, ConnectionClosedError, OSError, aio.TimeoutError)
            ),
        )
        return await retry(self._acquire)()

    async def _acquire(self) -> WebsocketConnection:
        async with self._lock:
            if self._closed:
                raise ConnectionPoolUnavailableError("Connection pool is closed")

            # Try to reuse existing available connections
            while self._available:
                connection = self._available.popleft()

                if connection.is_connected and not connection._closed:
                    try:
                        await connection.acquire()

                        # Health check the connection
                        try:
                            await connection.ping()
                            self._busy.add(connection)
                            logger.debug(f"Reused connection from pool: " f"{connection}")
                            return connection
                        except (ConnectionClosedError, ConnectionUnavailableError):
                            await connection.release()
                            await self._remove_connection(connection)
                            continue

                    except (ConnectionBusyError, ConnectionClosedError, ConnectionUnavailableError):
                        # Connection is no longer usable
                        await self._remove_connection(connection)
                        continue
                else:
                    # Connection is not healthy
                    await self._remove_connection(connection)

            # Create new connection if under limit
            if self._total >= self._max_connections:
                raise ConnectionPoolExhaustedError(
                    f"Maximum connections {self._max_connections} reached. "
                    f"Available: {len(self._available)}, "
                    f"Busy: {len(self._busy)}, "
                    f"Pending: {len(self._pending)}"
                )

            connection = self._create_connection()

            try:
                # Connect and acquire in one operation to avoid race conditions
                await aio.wait_for(connection.connect(), timeout=self._connection_timeout)
                await connection.acquire()

                self._busy.add(connection)
                self._total += 1

                logger.debug(f"Created new connection: {connection}")
                return connection

            except Exception as e:
                await connection.close()
                logger.error(f"Failed to create connection: {e}")
                raise ConnectionUnavailableError(f"Failed to create connection: {e}")

    async def acquire_new(self) -> WebsocketConnection:
        """Force acquire a new connection, avoiding reuse of existing
        connections.

        This method always creates a fresh connection and returns it in
        acquired  state, similar to acquire() but without attempting to reuse
        existing connections.

        Returns:
            A newly created and acquired WebsocketConnection.

        Raises:
            ConnectionPoolUnavailableError: If the pool is closed.
            ConnectionPoolExhaustedError:
                If maximum connections limit is reached.
            ConnectionUnavailableError:
                If connection creation fails after retries.
        """
        if not self._started:
            await self.start()

        retry = tenacity.retry(
            stop=tenacity.stop_after_attempt(self._max_retries),
            wait=tenacity.wait_exponential(multiplier=1, max=10),
            retry=tenacity.retry_if_exception_type(
                (ConnectionUnavailableError, ConnectionClosedError, OSError, aio.TimeoutError)
            ),
        )
        return await retry(self._acquire_new)()

    async def _acquire_new(self) -> WebsocketConnection:
        """Internal method to force create a new connection"""
        async with self._lock:
            if self._closed:
                raise ConnectionPoolUnavailableError("Connection pool is closed")

            # Check if we can create a new connection
            if self._total >= self._max_connections:
                raise ConnectionPoolExhaustedError(
                    f"Maximum connections {self._max_connections} reached. "
                    f"Available: {len(self._available)}, "
                    f"Busy: {len(self._busy)}, "
                    f"Pending: {len(self._pending)}"
                )

            connection = self._create_connection()

            try:
                # Connect and acquire in one operation to avoid race conditions
                await aio.wait_for(connection.connect(), timeout=self._connection_timeout)
                await connection.acquire()

                self._busy.add(connection)
                self._total += 1

                logger.debug(f"Force created new connection: {connection}")
                return connection

            except Exception as e:
                await connection.close()
                logger.error(f"Failed to force create connection: {e}")
                raise ConnectionUnavailableError(f"Failed to create " f"connection: {e}")

    async def _remove_connection(self, connection: WebsocketConnection) -> None:
        """Remove and close a connection, updating counters"""
        was_tracked = False

        if connection in self._busy:
            self._busy.remove(connection)
            was_tracked = True

        if connection in self._available:
            self._available.remove(connection)
            was_tracked = True

        # Remove from pending connections
        pending_to_remove = []
        for pending_id, pending_conn in self._pending.items():
            if pending_conn.connection == connection:
                pending_to_remove.append(pending_id)
                was_tracked = True

        for pending_id in pending_to_remove:
            pending_conn = self._pending.pop(pending_id)
            if pending_conn.drain_task and not pending_conn.drain_task.done():
                pending_conn.drain_task.cancel()

        if was_tracked:
            self._total -= 1

        try:
            await connection.close()
        except Exception as e:
            logger.warning(f"Error closing connection during removal: {e}")

    async def _drain_connection(self, pending_conn: PendingConnection) -> None:
        """Background task to drain server data from a connection.

        This task continuously receives data from the websocket until either:
        1. No data is received for drain_quiet_period seconds
        2. The drain_timeout is reached
        3. An error occurs

        If the connection is successfully drained, it's moved to available
        pool.Otherwise, it's removed from the pool.
        """
        connection = pending_conn.connection
        start_time = time.time()
        last_message_time = start_time
        drained_messages = 0

        logger.debug(f"Starting drain task for connection {connection}")

        try:
            while True:
                current_time = time.time()

                # Check if we've exceeded the overall drain timeout
                if current_time - start_time > pending_conn.drain_timeout:
                    logger.debug(f"Drain timeout reached for connection " f"{connection}")
                    break

                # Check if we've been quiet for the required period
                if current_time - last_message_time > self._drain_quiet_period:
                    logger.debug(
                        f"Quiet period reached for connection {connection}, " f"moving to available"
                    )

                    # Connection is clean, move it to available
                    async with self._lock:
                        if pending_conn.pending_id in self._pending:
                            self._pending.pop(pending_conn.pending_id)
                            if connection.is_connected and not connection._closed:
                                self._available.append(connection)
                                logger.debug(
                                    f"Moved drained connection to " f"available: {connection}"
                                )
                            else:
                                logger.debug(
                                    f"Connection not connected during "
                                    f"drain completion: {connection}"
                                )
                                await self._remove_connection(connection)
                    return

                # Try to receive data with a short timeout
                try:
                    recv_timeout = min(0.5, self._drain_quiet_period / 2)
                    if connection.websocket is None:
                        raise ConnectionUnavailableError(
                            f"Connection {connection} is not connected"
                        )
                    message = await aio.wait_for(connection.websocket.recv(), timeout=recv_timeout)

                    last_message_time = current_time
                    drained_messages += 1

                    # Check if this message matches our drain condition
                    if pending_conn.drain_condition(message):
                        logger.debug(
                            f"Drained server message from " f"{connection}: {str(message)[:100]}..."
                        )
                        continue
                    else:
                        # Message doesn't match drain condition,
                        # connection not clean
                        logger.debug(
                            f"Received unexpected message during drain from "
                            f"{connection}: {str(message)[:100]}..."
                        )
                        break

                except aio.TimeoutError:
                    # No data received within timeout, continue checking
                    continue

                except Exception as e:
                    logger.debug(f"Error during drain process for {connection}: {e}")
                    break

        except Exception as e:
            logger.debug(f"Unexpected error in drain task for {connection}: {e}")

        finally:
            # Connection is not clean or an error occurred, remove it
            logger.debug(
                f"Removing connection after drain task: {connection}, "
                f"messages drained: {drained_messages}"
            )

            async with self._lock:
                if pending_conn.pending_id in self._pending:
                    self._pending.pop(pending_conn.pending_id)
                await self._remove_connection(connection)

    async def release(self, connection: WebsocketConnection, *, force_remove: bool = False) -> None:
        """Release a connection back to the pool.

        The connection will be either:
        1. Returned to the available pool immediately if data draining is
           disabled
        2. Put into pending state for background draining if data draining is
           enabled
        3. Removed from the pool if force_remove is True or the connection is
           unhealthy

        Args:
            connection: The WebsocketConnection to release.
            force_remove: If True, the connection will be removed from the pool
                regardless of its state. Defaults to False.
        """
        async with self._lock:
            if connection not in self._busy:
                logger.warning(
                    f"Attempting to release connection not in busy set: " f"{connection}"
                )
                return

            self._busy.remove(connection)

            try:
                await connection.release()

                if force_remove or not connection.is_connected:
                    await self._remove_connection(connection)
                    logger.debug(f"Removed connection from pool: {connection}")
                    return

                # Check if connection is healthy
                if not connection.is_connected or self._closed:
                    await self._remove_connection(connection)
                    logger.debug(f"Removed unhealthy connection from pool: {connection}")
                    return

                # If we don't need to check for server data, directly
                # return to available
                if not self._check_server_data_on_release:
                    self._available.append(connection)
                    logger.debug(f"Released connection directly to available: " f"{connection}")
                    return

                # Put connection into pending state for background draining
                pending_conn = PendingConnection(
                    connection=connection,
                    drain_timeout=self._drain_timeout,
                    drain_condition=self._drain_condition,
                )

                self._pending[pending_conn.pending_id] = pending_conn

                # Start background drain task
                pending_conn.drain_task = aio.create_task(self._drain_connection(pending_conn))

                logger.debug(f"Put connection into pending state for draining: " f"{connection}")

            except Exception as e:
                logger.warning(f"Error releasing connection: {e}")
                await self._remove_connection(connection)

    @contextlib.asynccontextmanager
    async def get_connection(self) -> t.AsyncIterator[WebsocketConnection]:
        """Get a connection from the pool as an async context manager.

        The connection will be automatically released back to the pool when
        the context manager exits.

        Yields:
            A WebsocketConnection from the pool.

        Raises:
            ConnectionPoolUnavailableError: If the pool is closed.
            ConnectionPoolExhaustedError:
                If maximum connections limit is reached.
            ConnectionUnavailableError: If connection acquisition fails.
        """
        connection = await self.acquire()
        try:
            yield connection
        finally:
            await self.release(connection)

    @contextlib.asynccontextmanager
    async def get_new_connection(self) -> t.AsyncIterator[WebsocketConnection]:
        """Get a new connection from the pool as an async context manager.

        Forces creation of a new connection without reusing existing ones.
        The connection will be automatically released back to the pool when
        the context manager exits.

        Yields:
            A newly created WebsocketConnection.

        Raises:
            ConnectionPoolUnavailableError: If the pool is closed.
            ConnectionPoolExhaustedError:
                If maximum connections limit is reached.
            ConnectionUnavailableError: If connection creation fails.
        """
        connection = await self.acquire_new()
        try:
            yield connection
        finally:
            await self.release(connection)

    async def _cleanup_loop(self) -> None:
        try:
            while not self._closed:
                await aio.sleep(self._cleanup_interval)
                await self._cleanup_idle()
        except aio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in cleanup loop: {e}")

    async def _cleanup_idle(self) -> None:
        async with self._lock:
            current_time = time.time()

            # Clean up available connections
            to_remove = []
            for conn in list(self._available):
                if (
                    not conn.is_connected
                    or (current_time - conn.last_activity) > self._idle_timeout
                ):
                    to_remove.append(conn)

            for conn in to_remove:
                self._available.remove(conn)
                self._total -= 1
                try:
                    await conn.close()
                except Exception as e:
                    logger.warning(f"Error closing idle connection: {e}")
                logger.debug(f"Cleaned up idle connection: {conn}")

            # Clean up busy connections that are no longer connected
            busy_to_remove = []
            for conn in list(self._busy):
                if not conn.is_connected:
                    busy_to_remove.append(conn)

            for conn in busy_to_remove:
                self._busy.remove(conn)
                self._total -= 1
                try:
                    await conn.close()
                except Exception as e:
                    logger.warning(f"Error closing disconnected connection: {e}")
                logger.warning(f"Cleaned up disconnected busy connection: {conn}")

            # Clean up pending connections that have timed out or
            # are no longer connected
            pending_to_remove = []
            for pending_id, pending_conn in self._pending.items():
                conn = pending_conn.connection

                # Check if connection is no longer connected
                if not conn.is_connected:
                    pending_to_remove.append(pending_id)
                    continue

                # Check if pending connection has been around too long
                if (current_time - pending_conn.created_at) > (
                    self._drain_timeout + self._cleanup_interval
                ):
                    pending_to_remove.append(pending_id)
                    continue

            for pending_id in pending_to_remove:
                pending_conn = self._pending.pop(pending_id)

                # Cancel the drain task if it's still running
                if pending_conn.drain_task and not pending_conn.drain_task.done():
                    pending_conn.drain_task.cancel()

                self._total -= 1
                try:
                    await pending_conn.connection.close()
                except Exception as e:
                    logger.warning(f"Error closing timed out pending connection: {e}")
                logger.debug(
                    f"Cleaned up timed out pending connection: " f"{pending_conn.connection}"
                )

    async def close_all(self) -> None:
        """Close all connections and shut down the pool.

        Stops the cleanup task and closes all connections in the pool.
        After calling this method, the pool cannot be used again.
        """
        async with self._lock:
            if self._closed:
                return

            self._closed = True

            # Cancel cleanup task
            if self._cleanup_task and not self._cleanup_task.done():
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except aio.CancelledError:
                    pass
                self._cleanup_task = None

            # Close all available connections
            while self._available:
                conn = self._available.popleft()
                try:
                    await conn.close()
                except Exception as e:
                    logger.warning(f"Error closing available connection: {e}")

            # Close all busy connections
            for conn in list(self._busy):
                try:
                    await conn.close()
                except Exception as e:
                    logger.warning(f"Error closing busy connection: {e}")
            self._busy.clear()

            # Close all pending connections and cancel their drain tasks
            for pending_id, pending_conn in self._pending.items():
                if pending_conn.drain_task and not pending_conn.drain_task.done():
                    pending_conn.drain_task.cancel()
                try:
                    await pending_conn.connection.close()
                except Exception as e:
                    logger.warning(f"Error closing pending connection: {e}")
            self._pending.clear()

            self._total = 0

        logger.info(f"Closed WebSocket connection pool for {self.uri}")

    def __len__(self) -> int:
        return self._total

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"uri={self.uri}, "
            f"total={self._total}, "
            f"available={len(self._available)}, "
            f"busy={len(self._busy)}, "
            f"pending={len(self._pending)}, "
            f"closed={self._closed})"
        )

    __str__ = __repr__

    async def __aenter__(self) -> t.Self:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> t.Literal[False]:
        await self.close_all()
        return False


__all__ = [
    "ConnectionPoolUnavailableError",
    "ConnectionPoolExhaustedError",
    "WebsocketConnectionPool",
    "PendingConnection",
]
