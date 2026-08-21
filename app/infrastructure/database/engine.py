"""SQLAlchemy async engine factory with connection pooling."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def normalize_database_url(url: str) -> str:
    """Ensure SQLAlchemy asyncpg dialect is used."""
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgres://")
    return url


def create_db_engine(settings: Settings | None = None) -> AsyncEngine:
    """
    Create an async SQLAlchemy engine backed by a connection pool.

    Pool settings come from YAML/Settings:
    - ``pool_size``: persistent connections
    - ``max_overflow``: extra burst connections
    - ``pool_pre_ping``: drop stale connections
    """
    cfg = settings or get_settings()
    url = normalize_database_url(cfg.database_url)
    engine = create_async_engine(
        url,
        echo=cfg.database_echo,
        pool_size=cfg.database_pool_size,
        max_overflow=cfg.database_max_overflow,
        pool_timeout=cfg.database_pool_timeout,
        pool_recycle=cfg.database_pool_recycle,
        pool_pre_ping=True,
    )
    logger.info(
        "database engine created pool_size=%s max_overflow=%s",
        cfg.database_pool_size,
        cfg.database_max_overflow,
    )
    return engine
