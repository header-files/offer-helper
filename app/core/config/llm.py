"""LLM configuration models (loaded from YAML; secrets resolved via Settings)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

LLMProvider = Literal["auto", "openai", "deepseek"]


class LLMModelConfig(BaseModel):
    """
    One chat-model endpoint.

    Required: ``model``. Optional infrastructure fields:
    ``base_url`` (overridable by ``LLM_<NAME>_BASE_URL``),
    ``provider`` (``auto`` / ``openai`` / ``deepseek``).

    Any other keys are forwarded as client constructor kwargs
    (e.g. ``temperature``, ``timeout``, ``max_retries``, ``top_p``,
    ``extra_body``, ...). Adding parameters only requires YAML changes.
    """

    model_config = ConfigDict(extra="allow")

    model: str
    base_url: str = ""
    provider: LLMProvider = "auto"

    def chat_openai_kwargs(self) -> dict[str, Any]:
        """
        Build kwargs for ChatOpenAI / ChatDeepSeek.

        Excludes infrastructure fields (``base_url``, ``provider``).
        Drops ``None`` values so the client keeps its own defaults.
        """
        data = self.model_dump(exclude_none=True)
        data.pop("base_url", None)
        data.pop("provider", None)
        return data


class LLMSettings(BaseModel):
    """Multi-model LLM registry settings."""

    default: str = "chat"
    models: dict[str, LLMModelConfig] = Field(default_factory=dict)
