"""Unit tests for database URL normalization and pool wiring."""

from __future__ import annotations

import pytest
from sqlalchemy.pool import AsyncAdaptedQueuePool

from app.core.config import Settings
from app.core.exceptions import DatabaseNotInitializedError
from app.infrastructure.database import (
    create_db_engine,
    get_engine,
    normalize_database_url,
)


def test_normalize_database_url_adds_asyncpg_dialect() -> None:
    assert (
        normalize_database_url("postgresql://user:pass@localhost:5432/db")
        == "postgresql+asyncpg://user:pass@localhost:5432/db"
    )
    assert (
        normalize_database_url("postgres://user:pass@localhost:5432/db")
        == "postgresql+asyncpg://user:pass@localhost:5432/db"
    )
    assert (
        normalize_database_url("postgresql+asyncpg://user:pass@localhost:5432/db")
        == "postgresql+asyncpg://user:pass@localhost:5432/db"
    )


def test_create_db_engine_uses_queue_pool() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://testuser:testpassword@localhost:5432/testdb",
        database_pool_size=7,
        database_max_overflow=3,
        database_echo=False,
    )
    engine = create_db_engine(settings)
    try:
        pool = engine.sync_engine.pool
        assert isinstance(pool, AsyncAdaptedQueuePool)
        assert pool.size() == 7
    finally:
        engine.sync_engine.dispose()


def test_get_engine_before_startup_raises() -> None:
    with pytest.raises(DatabaseNotInitializedError):
        get_engine()
