"""FastAPI application factory and entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.middleware import TraceIdMiddleware
from app.api.routers import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.infrastructure.database import init_db, shutdown_db
from app.infrastructure.redis import init_redis, shutdown_redis


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncIterator[None]:
    """Initialize and tear down process-wide infrastructure."""
    configure_logging()
    await init_db()
    await init_redis()
    yield
    await shutdown_redis()
    await shutdown_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    configure_logging(settings)
    application = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(TraceIdMiddleware)
    application.include_router(api_router)
    return application


app = create_app()
