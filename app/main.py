"""FastAPI application factory and entrypoint."""

from fastapi import FastAPI

from app.api.routers import api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
    )
    application.include_router(api_router)
    return application


app = create_app()
