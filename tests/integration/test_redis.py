"""Integration tests against local Redis at redis://localhost:6379."""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator

import pytest

from app.infrastructure.redis import RedisClient, create_redis

LOCAL_REDIS_URL = "redis://localhost:6379/0"
KEY_PREFIX = "offer-helper:test:phase1:"


@pytest.fixture
async def redis_client() -> AsyncIterator[RedisClient]:
    connection = create_redis(
        LOCAL_REDIS_URL,
        socket_timeout=5.0,
        max_connections=30,
        decode_responses=True,
    )
    client = RedisClient(
        connection,
        max_connections=30,
        command_timeout=10.0,
        default_ttl=60,
    )
    await client.ping()
    yield client
    await client.close()


async def test_local_redis_ping_set_get_delete(redis_client: RedisClient) -> None:
    key = f"{KEY_PREFIX}{uuid.uuid4()}"
    value = "offer-helper-redis-ok"
    try:
        assert await redis_client.ping() is True
        assert await redis_client.set(key, value, ex=30) is True
        assert await redis_client.get(key) == value
        assert await redis_client.delete(key) == 1
        assert await redis_client.get(key) is None
    finally:
        await redis_client.delete(key)


async def test_local_redis_connection_pool_handles_concurrency(
    redis_client: RedisClient,
) -> None:
    key = f"{KEY_PREFIX}{uuid.uuid4()}"
    try:
        await redis_client.set(key, "concurrent", ex=30)
        results = await asyncio.gather(*[redis_client.get(key) for _ in range(24)])
        assert results == ["concurrent"] * 24
        pool = redis_client.backend.connection_pool
        assert pool.max_connections == 30
    finally:
        await redis_client.delete(key)


async def test_local_redis_reports_standalone_mode(redis_client: RedisClient) -> None:
    info = await redis_client.backend.info("server")
    assert redis_client.mode.value == "standalone"
    assert info["redis_mode"] == "standalone"
    assert info["redis_version"]
