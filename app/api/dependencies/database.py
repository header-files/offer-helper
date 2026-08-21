"""Database-related FastAPI dependencies."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_session_factory


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped async SQLAlchemy session."""
    factory = get_session_factory()
    async with factory() as session:
        yield session
