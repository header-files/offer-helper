"""Redis client factory: standalone, Sentinel, and Cluster with connection pools."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import parse_qs, unquote, urlparse

from redis.asyncio import Redis
from redis.asyncio.cluster import ClusterNode, RedisCluster
from redis.asyncio.connection import ConnectionPool
from redis.asyncio.sentinel import Sentinel

from app.core.exceptions import UnsupportedRedisSchemeError
from app.core.logging import get_logger

logger = get_logger(__name__)

RedisBackend = Redis | RedisCluster


class RedisMode(StrEnum):
    STANDALONE = "standalone"
    SENTINEL = "sentinel"
    CLUSTER = "cluster"


@dataclass(frozen=True, slots=True)
class RedisConnectionParams:
    """Pool and timeout settings shared by all Redis topologies."""

    socket_timeout: float = 5.0
    max_connections: int = 30
    decode_responses: bool = True


@dataclass(frozen=True, slots=True)
class RedisConnection:
    backend: RedisBackend
    mode: RedisMode

    async def aclose(self) -> None:
        backend = self.backend
        if isinstance(backend, RedisCluster):
            await backend.aclose()
            return
        await backend.aclose(close_connection_pool=True)


def _parse_host_port(node: str) -> tuple[str, int]:
    stripped = node.strip()
    if not stripped:
        msg = "Empty Redis node address"
        raise ValueError(msg)
    if stripped.startswith("[") and "]" in stripped:
        host, rest = stripped[1:].split("]", 1)
        if not rest.startswith(":"):
            msg = f"Invalid Redis node address: {node}"
            raise ValueError(msg)
        return host, int(rest[1:])
    host, sep, port = stripped.rpartition(":")
    if not sep or not host:
        msg = f"Invalid Redis node address: {node}"
        raise ValueError(msg)
    return host, int(port)


def _query_nodes(query: dict[str, list[str]], key: str) -> tuple[tuple[str, int], ...]:
    raw = query.get(key, [""])[0]
    if not raw:
        return ()
    return tuple(_parse_host_port(item) for item in raw.split(",") if item.strip())


def _create_standalone(url: str, params: RedisConnectionParams) -> Redis:
    pool = ConnectionPool.from_url(
        url,
        max_connections=params.max_connections,
        socket_timeout=params.socket_timeout,
        decode_responses=params.decode_responses,
    )
    return Redis(connection_pool=pool)


def _create_sentinel(url: str, params: RedisConnectionParams) -> Redis:
    parsed = urlparse(url)
    password = unquote(parsed.password) if parsed.password else None
    service_name = parsed.hostname
    if not service_name:
        msg = "Sentinel URL must include the master service name as host"
        raise ValueError(msg)

    query = parse_qs(parsed.query)
    sentinels = _query_nodes(query, "sentinels")
    if not sentinels:
        msg = "Sentinel URL requires ?sentinels=host:port[,host:port]"
        raise ValueError(msg)

    sentinel = Sentinel(
        sentinels,
        password=password,
        socket_timeout=params.socket_timeout,
    )
    return sentinel.master_for(
        service_name=service_name,
        password=password,
        max_connections=params.max_connections,
        decode_responses=params.decode_responses,
        socket_timeout=params.socket_timeout,
    )


def _create_cluster(url: str, params: RedisConnectionParams) -> RedisCluster:
    parsed = urlparse(url)
    password = unquote(parsed.password) if parsed.password else None
    username = unquote(parsed.username) if parsed.username else None
    ssl = parsed.scheme in {"rediss+cluster", "rediss-cluster"}

    query = parse_qs(parsed.query)
    extra_nodes = _query_nodes(query, "nodes")

    host = parsed.hostname
    port = parsed.port or 6379
    if not host:
        msg = "Cluster URL must include a startup host"
        raise ValueError(msg)

    startup_nodes = [ClusterNode(host, port), *(ClusterNode(h, p) for h, p in extra_nodes)]
    return RedisCluster(
        startup_nodes=startup_nodes,
        username=username,
        password=password,
        ssl=ssl,
        max_connections=params.max_connections,
        decode_responses=params.decode_responses,
        socket_timeout=params.socket_timeout,
    )


def create_redis(
    url: str,
    socket_timeout: float = 5.0,
    max_connections: int = 30,
    decode_responses: bool = True,
) -> RedisConnection:
    """
    Create an async Redis client from URL.

    - Standalone: ``redis://[:password@]host:6379/0`` (also ``rediss://``)
    - Sentinel: ``sentinel://[:password@]mymaster?sentinels=host1:26379,host2:26379``
    - Cluster: ``cluster://[:password@]host:6379[?nodes=host2:6379,host3:6379]``
      (aliases: ``redis+cluster://``, ``rediss+cluster://``)
    """
    params = RedisConnectionParams(
        socket_timeout=socket_timeout,
        max_connections=max_connections,
        decode_responses=decode_responses,
    )
    scheme = urlparse(url).scheme.lower()

    if scheme in {"redis", "rediss"}:
        connection = RedisConnection(_create_standalone(url, params), RedisMode.STANDALONE)
    elif scheme == "sentinel":
        connection = RedisConnection(_create_sentinel(url, params), RedisMode.SENTINEL)
    elif scheme in {"cluster", "redis+cluster", "rediss+cluster", "redis-cluster"}:
        connection = RedisConnection(_create_cluster(url, params), RedisMode.CLUSTER)
    else:
        logger.warning("redis client creation failed: unsupported scheme %s", scheme)
        msg = f"Unsupported Redis scheme: {scheme or '<empty>'}"
        raise UnsupportedRedisSchemeError(msg)

    logger.info(
        "redis client created mode=%s max_connections=%s",
        connection.mode,
        params.max_connections,
    )
    return connection
