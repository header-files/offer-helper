"""Database infrastructure exceptions."""

from app.core.exceptions.base import AppError


class DatabaseInfrastructureError(AppError):
    """Raised when database client construction or access fails."""


class DatabaseNotInitializedError(DatabaseInfrastructureError):
    """Raised when the database engine is accessed before application startup."""
