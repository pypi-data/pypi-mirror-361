# aio-websocket-pool

A flexible, async-friendly WebSocket connection pool implementation for Python with connection reuse, health monitoring,
and automatic cleanup.

## Features

- **Connection Reuse**: Efficient connection pooling with automatic reuse of healthy connections
- **Health Monitoring**: Automatic connection health checks and cleanup of disconnected connections
- **Thread-safe**: Uses asyncio locks for concurrent access in async environments
- **Configurable Limits**: Set maximum connection limits and timeouts
- **Retry Logic**: Built-in exponential backoff retry mechanism for connection failures
- **Server Data Draining**: Optional server data detection and draining during connection release
- **Context Manager Support**: Clean, intuitive API with async context managers
- **Idle Connection Cleanup**: Automatic cleanup of idle connections to prevent resource leaks
- **Type-safe**: Full typing support with comprehensive type hints

## Installation

```bash
pip install aio-websocket-pool
```

Or using Poetry:

```bash
poetry add aio-websocket-pool
```

## Quick Start

```python
import asyncio
from aio_websocket_pool import WebsocketConnectionPool


async def main():
    # Create a connection pool
    async with WebsocketConnectionPool(uri="ws://localhost:8080") as pool:
        # Get a connection from the pool
        async with pool.get_connection() as conn:
            await conn.send("Hello, World!")
            response = await conn.recv()
            print(response)


asyncio.run(main())
```

## Advanced Usage

### Basic Pool Configuration

```python
from aio_websocket_pool import WebsocketConnectionPool

# Create a pool with custom configuration
pool = WebsocketConnectionPool(
    uri="ws://localhost:8080",
    max_connections=10,
    idle_timeout=60.0,
    connection_timeout=10.0,
    max_retries=3,
    warmup_connections=2,  # Pre-create 2 connections
    headers={"Authorization": "Bearer token123"}
)

async with pool:
    # Pool is ready to use
    conn = await pool.acquire()
    try:
        await conn.send("Hello")
        response = await conn.recv()
        print(response)
    finally:
        await pool.release(conn)
```

### Connection Health Monitoring

```python
# Enable server data checking during connection release
pool = WebsocketConnectionPool(
    uri="ws://localhost:8080",
    check_server_data_on_release=True,
    drain_timeout=5.0,
    drain_quiet_period=1.0
)

async with pool:
    async with pool.get_connection() as conn:
        await conn.send("REQUEST")
        response = await conn.recv()
        print(response)
        # Connection will be checked for additional server data
        # before being returned to the pool
```

### Custom Drain Condition

```python
def custom_drain_condition(message):
    # Only drain messages that look like server notifications
    return message.startswith(b'{"type":"notification"')


pool = WebsocketConnectionPool(
    uri="ws://localhost:8080",
    check_server_data_on_release=True,
    drain_condition=custom_drain_condition
)
```

### Force New Connection

```python
async with pool:
    # Force create a new connection instead of reusing existing ones
    async with pool.get_new_connection() as conn:
        await conn.send("Important message")
        response = await conn.recv()
        print(response)
```

### Connection Pool Monitoring

```python
async with pool:
    print(f"Total connections: {pool.total_connections}")
    print(f"Available connections: {pool.available_connections}")
    print(f"Busy connections: {pool.busy_connections}")
    print(f"Pending connections: {pool.pending_connections}")
```

### Manual Connection Management

```python
async with pool:
    # Manually acquire and release connections
    conn = await pool.acquire()
    try:
        await conn.send("Hello")
        response = await conn.recv()
        print(response)
    finally:
        # Release connection back to pool
        await pool.release(conn)

    # Force remove a connection from the pool
    conn = await pool.acquire()
    try:
        await conn.send("Hello")
        response = await conn.recv()
        print(response)
    finally:
        # Remove connection instead of returning to pool
        await pool.release(conn, force_remove=True)
```

## API Reference

### WebsocketConnectionPool

#### Constructor

```
WebsocketConnectionPool(
    uri: str,
    headers: Dict[str, str] | None = None,
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
    **kwargs
)
```

Creates a new WebSocket connection pool.

#### Properties

- `total_connections: int` - Total number of connections in the pool
- `available_connections: int` - Number of available connections
- `busy_connections: int` - Number of connections currently in use
- `pending_connections: int` - Number of connections being drained
- `is_closed: bool` - Whether the pool is closed
- `is_started: bool` - Whether the pool has been started

#### Methods

- `async start()` - Start the connection pool
- `async acquire() -> WebsocketConnection` - Acquire a connection from the pool
- `async acquire_new() -> WebsocketConnection` - Force acquire a new connection
- `async release(connection, *, force_remove=False)` - Release a connection back to the pool
- `async get_connection()` - Context manager for acquiring/releasing connections
- `async get_new_connection()` - Context manager for acquiring/releasing new connections
- `async close_all()` - Close all connections and shut down the pool

### WebsocketConnection

#### Properties

- `is_busy: bool` - Whether the connection is currently in use
- `is_draining: bool` - Whether the connection is being drained
- `is_connected: bool` - Whether the connection is active
- `last_activity: float` - Timestamp of last activity

#### Methods

- `async send(message: str | bytes)` - Send a message through the connection
- `async recv() -> str | bytes` - Receive a message from the connection
- `async ping()` - Send a ping to check connection health
- `async connect()` - Establish the WebSocket connection
- `async close()` - Close the connection

## Error Handling

The library provides several specific exception types:

```python
from aio_websocket_pool import (
    WebsocketError,
    ConnectionBusyError,
    ConnectionUnavailableError,
    ConnectionClosedError,
    ConnectionPoolExhaustedError,
    ConnectionPoolUnavailableError,
)

try:
    async with pool.get_connection() as conn:
        await conn.send("Hello")
        response = await conn.recv()
except ConnectionPoolExhaustedError:
    print("No connections available in pool")
except ConnectionClosedError:
    print("Connection was closed unexpectedly")
except WebsocketError as e:
    print(f"WebSocket error: {e}")
```

## Configuration Best Practices

### For High-Traffic Applications

```python
pool = WebsocketConnectionPool(
    uri="ws://your-server.com/ws",
    max_connections=100,
    warmup_connections=10,
    idle_timeout=120.0,
    connection_timeout=5.0,
    max_retries=5,
    cleanup_interval=10.0
)
```

### For Low-Latency Applications

```python
pool = WebsocketConnectionPool(
    uri="ws://your-server.com/ws",
    max_connections=50,
    warmup_connections=5,
    idle_timeout=30.0,
    connection_timeout=3.0,
    check_server_data_on_release=True,
    drain_timeout=2.0,
    drain_quiet_period=0.5
)
```

### For Resource-Constrained Environments

```python
pool = WebsocketConnectionPool(
    uri="ws://your-server.com/ws",
    max_connections=5,
    warmup_connections=1,
    idle_timeout=30.0,
    connection_timeout=10.0,
    max_retries=2,
    cleanup_interval=5.0
)
```

## Requirements

- Python 3.11+
- websockets >= 15.0.1
- tenacity >= 9.1.2

## License

This project is licensed under the MIT License.

## Development

### Setup

```bash
poetry install
```

### Running Tests

```bash
poetry run pytest
```

### Code Quality

```bash
poetry run black .
poetry run isort .
poetry run flake8 .
poetry run mypy .
```

### Building

```bash
poetry build
```