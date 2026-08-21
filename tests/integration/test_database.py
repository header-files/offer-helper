"""Integration tests against local PostgreSQL at localhost:5432."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import Settings
from app.infrastructure.database import (
    create_db_engine,
    init_db,
    ping_db,
    session_scope,
    shutdown_db,
)

LOCAL_DATABASE_URL = "postgresql+asyncpg://testuser:testpassword@localhost:5432/testdb"


@pytest.fixture
def local_db_settings() -> Settings:
    return Settings(
        database_url=LOCAL_DATABASE_URL,
        database_pool_size=5,
        database_max_overflow=5,
        database_echo=False,
    )


@pytest.fixture
async def db_engine(local_db_settings: Settings) -> AsyncIterator[AsyncEngine]:
    engine = create_db_engine(local_db_settings)
    await ping_db(engine)
    yield engine
    await engine.dispose()


async def test_local_postgres_ping(db_engine: AsyncEngine) -> None:
    assert await ping_db(db_engine) is True


async def test_local_postgres_select_version(db_engine: AsyncEngine) -> None:
    async with db_engine.connect() as connection:
        version = await connection.scalar(text("SHOW server_version"))
    assert version is not None
    assert str(version).startswith("18.")


async def test_local_postgres_pool_handles_concurrency(db_engine: AsyncEngine) -> None:
    async def one_query() -> int:
        async with db_engine.connect() as connection:
            value = await connection.scalar(text("SELECT 1"))
            assert value is not None
            return int(value)

    results = await asyncio.gather(*[one_query() for _ in range(12)])
    assert results == [1] * 12


async def test_init_db_and_session_scope(local_db_settings: Settings) -> None:
    await init_db(local_db_settings)
    try:
        async with session_scope() as session:
            value = await session.scalar(text("SELECT current_database()"))
            assert value == "testdb"
    finally:
        await shutdown_db()
