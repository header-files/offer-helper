"""Process-wide async database engine and session factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.core.config import Settings, get_settings
from app.core.exceptions import DatabaseNotInitializedError
from app.core.logging import get_logger
from app.infrastructure.database.engine import create_db_engine

logger = get_logger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_db(settings: Settings | None = None) -> AsyncEngine:
    """Create the process-wide engine/session factory and verify connectivity."""
    global _engine, _session_factory
    cfg = settings or get_settings()
    engine = create_db_engine(cfg)
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    try:
        await ping_db(engine)
    except Exception:
        await engine.dispose()
        raise
    _engine = engine
    _session_factory = session_factory
    logger.info("database connected")
    return _engine


async def shutdown_db() -> None:
    """Dispose the process-wide engine and clear session factory."""
    global _engine, _session_factory
    if _engine is None:
        return
    await _engine.dispose()
    _engine = None
    _session_factory = None
    logger.info("database disconnected")


def get_engine() -> AsyncEngine:
    """Return the process-wide async engine."""
    if _engine is None:
        msg = "Database engine is not initialized; wait for application startup"
        raise DatabaseNotInitializedError(msg)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the process-wide async session factory."""
    if _session_factory is None:
        msg = "Database session factory is not initialized; wait for application startup"
        raise DatabaseNotInitializedError(msg)
    return _session_factory


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    """Provide a short-lived session with commit/rollback handling."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def ping_db(engine: AsyncEngine | None = None) -> bool:
    """Execute ``SELECT 1`` to verify pool connectivity."""
    target = engine or get_engine()
    async with target.connect() as connection:
        await connection.execute(text("SELECT 1"))
    return True
