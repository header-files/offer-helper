"""Application-level exceptions."""

from app.core.exceptions.base import AppError
from app.core.exceptions.database import (
    DatabaseInfrastructureError,
    DatabaseNotInitializedError,
)
from app.core.exceptions.llm import (
    LLMConfigError,
    LLMInfrastructureError,
    LLMModelNotFoundError,
)
from app.core.exceptions.redis import (
    RedisInfrastructureError,
    RedisNotInitializedError,
    UnsupportedRedisSchemeError,
)

__all__ = [
    "AppError",
    "DatabaseInfrastructureError",
    "DatabaseNotInitializedError",
    "LLMConfigError",
    "LLMInfrastructureError",
    "LLMModelNotFoundError",
    "RedisInfrastructureError",
    "RedisNotInitializedError",
    "UnsupportedRedisSchemeError",
]
