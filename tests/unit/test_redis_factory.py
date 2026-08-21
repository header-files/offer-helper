"""Unit tests for Redis URL factory (no live server required)."""

from __future__ import annotations

import pytest
from redis.asyncio import Redis
from redis.asyncio.cluster import RedisCluster
from redis.asyncio.connection import ConnectionPool

from app.core.exceptions import RedisNotInitializedError, UnsupportedRedisSchemeError
from app.infrastructure.redis import RedisMode, create_redis, get_redis_client


async def test_standalone_url_uses_connection_pool() -> None:
    connection = create_redis(
        "redis://localhost:6379/0",
        max_connections=16,
        decode_responses=True,
    )
    backend = connection.backend
    try:
        assert connection.mode is RedisMode.STANDALONE
        assert isinstance(backend, Redis)
        pool = backend.connection_pool
        assert isinstance(pool, ConnectionPool)
        assert pool.max_connections == 16
    finally:
        await connection.aclose()


async def test_sentinel_url_parses_master_and_sentinels() -> None:
    connection = create_redis(
        "sentinel://:secret@mymaster?sentinels=10.0.0.1:26379,10.0.0.2:26379",
        max_connections=12,
    )
    backend = connection.backend
    try:
        assert connection.mode is RedisMode.SENTINEL
        assert isinstance(backend, Redis)
        pool = backend.connection_pool
        assert pool.max_connections == 12
        assert pool.connection_kwargs["password"] == "secret"
    finally:
        await connection.aclose()


async def test_cluster_url_builds_startup_nodes() -> None:
    connection = create_redis(
        "cluster://:cluster-pass@10.0.0.1:7000?nodes=10.0.0.2:7000,10.0.0.3:7000",
        max_connections=8,
    )
    backend = connection.backend
    try:
        assert connection.mode is RedisMode.CLUSTER
        assert isinstance(backend, RedisCluster)
        startup = backend.nodes_manager.startup_nodes
        addresses = set(startup.keys())
        assert addresses == {"10.0.0.1:7000", "10.0.0.2:7000", "10.0.0.3:7000"}
    finally:
        await connection.aclose()


def test_unsupported_scheme_raises() -> None:
    with pytest.raises(UnsupportedRedisSchemeError, match="http"):
        create_redis("http://localhost:6379")


def test_sentinel_url_requires_sentinels_query() -> None:
    with pytest.raises(ValueError, match="sentinels"):
        create_redis("sentinel://mymaster")


def test_get_redis_client_before_startup_raises() -> None:
    with pytest.raises(RedisNotInitializedError):
        get_redis_client()
