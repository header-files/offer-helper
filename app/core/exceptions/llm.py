"""LLM infrastructure exceptions."""

from app.core.exceptions.base import AppError


class LLMInfrastructureError(AppError):
    """Raised when LLM client construction or access fails."""


class LLMModelNotFoundError(LLMInfrastructureError):
    """Raised when a requested model name is not present in config."""


class LLMConfigError(LLMInfrastructureError):
    """Raised when LLM configuration is incomplete or invalid."""
