"""Redis infrastructure exceptions."""

from app.core.exceptions.base import AppError


class RedisInfrastructureError(AppError):
    """Raised when Redis client construction or access fails."""


class UnsupportedRedisSchemeError(RedisInfrastructureError):
    """Raised when REDIS_URL uses an unsupported scheme."""


class RedisNotInitializedError(RedisInfrastructureError):
    """Raised when Redis is accessed before application startup."""
