"""Redis client wrapper: connection-pool backend, concurrency limiter, timeouts."""

from __future__ import annotations

import asyncio
from typing import Any

from app.core.config import Settings, get_settings
from app.core.exceptions import RedisNotInitializedError
from app.core.logging import get_logger
from app.infrastructure.redis.factory import RedisConnection, RedisMode, create_redis

logger = get_logger(__name__)

_client: RedisClient | None = None


class RedisClient:
    """Application Redis facade. All I/O goes through the shared pool + semaphore."""

    def __init__(
        self,
        connection: RedisConnection,
        *,
        max_connections: int = 30,
        command_timeout: float = 60.0,
        default_ttl: int = 86400,
    ) -> None:
        self._connection = connection
        self._semaphore = asyncio.Semaphore(max(1, max_connections))
        self._command_timeout = command_timeout
        self._default_ttl = default_ttl

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> RedisClient:
        cfg = settings or get_settings()
        connection = create_redis(
            cfg.redis_url,
            socket_timeout=cfg.redis_socket_timeout,
            max_connections=cfg.redis_max_connections,
            decode_responses=cfg.redis_decode_responses,
        )
        return cls(
            connection,
            max_connections=cfg.redis_max_connections,
            command_timeout=cfg.redis_command_timeout,
            default_ttl=cfg.redis_default_ttl,
        )

    @property
    def mode(self) -> RedisMode:
        return self._connection.mode

    @property
    def backend(self) -> Any:
        return self._connection.backend

    async def _run(self, coro: Any, timeout: float | None) -> Any:
        limit = self._command_timeout if timeout is None else timeout
        async with self._semaphore:
            return await asyncio.wait_for(coro, limit)

    async def ping(self, timeout: float | None = None) -> bool:
        result = await self._run(self.backend.ping(), timeout)
        return bool(result)

    async def get(self, key: str, timeout: float | None = None) -> Any:
        return await self._run(self.backend.get(key), timeout)

    async def set(
        self,
        key: str,
        value: str,
        ex: int | None = None,
        timeout: float | None = None,
    ) -> Any:
        ttl = self._default_ttl if ex is None else ex
        return await self._run(self.backend.set(key, value, ex=ttl), timeout)

    async def delete(self, key: str, timeout: float | None = None) -> int:
        result = await self._run(self.backend.delete(key), timeout)
        return int(result)

    async def close(self) -> None:
        await self._connection.aclose()


async def init_redis(settings: Settings | None = None) -> RedisClient:
    """Create the process-wide Redis client and verify connectivity."""
    global _client
    _client = RedisClient.from_settings(settings)
    await _client.ping()
    logger.info("redis connected mode=%s", _client.mode)
    return _client


async def shutdown_redis() -> None:
    """Close the process-wide Redis client."""
    global _client
    if _client is None:
        return
    await _client.close()
    _client = None
    logger.info("redis disconnected")


def get_redis_client() -> RedisClient:
    """Return the process-wide Redis client. Must be called after startup."""
    if _client is None:
        msg = "Redis client is not initialized; wait for application startup"
        raise RedisNotInitializedError(msg)
    return _client
