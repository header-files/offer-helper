"""Chat model factory driven entirely by YAML + env secrets."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI

from app.core.config import Settings, get_settings
from app.core.config.llm import LLMModelConfig, LLMProvider
from app.core.exceptions import LLMConfigError, LLMModelNotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)


def list_llm_models(settings: Settings | None = None) -> list[str]:
    """Return configured model names."""
    cfg = settings or get_settings()
    return sorted(cfg.llm_models)


def get_llm_model_config(
    name: str | None = None,
    settings: Settings | None = None,
) -> LLMModelConfig:
    """Return the YAML config for a model name."""
    cfg = settings or get_settings()
    model_name = name or cfg.llm_default
    try:
        return cfg.get_llm_model_config(model_name)
    except KeyError as exc:
        raise LLMModelNotFoundError(str(exc)) from exc


def resolve_llm_provider(
    model_cfg: LLMModelConfig,
    *,
    base_url: str = "",
) -> LLMProvider:
    """
    Resolve which client to use.

    - ``provider: openai|deepseek`` in YAML wins
    - ``auto``: DeepSeek if ``model`` or ``base_url`` mentions deepseek
    """
    if model_cfg.provider != "auto":
        return model_cfg.provider

    model = model_cfg.model.lower()
    url = (base_url or model_cfg.base_url or "").lower()
    if "deepseek" in model or "deepseek" in url:
        return "deepseek"
    return "openai"


@lru_cache(maxsize=32)
def get_chat_model(name: str | None = None) -> BaseChatModel:
    """
    Build a chat client for the given configured model name.

    DeepSeek models use ``ChatDeepSeek`` (preserves ``reasoning_content``);
    other models use ``ChatOpenAI``. Selection is automatic from ``model`` /
    ``base_url``, or explicit via YAML ``provider``.
    """
    settings = get_settings()
    model_name = name or settings.llm_default
    try:
        model_cfg = settings.get_llm_model_config(model_name)
    except KeyError as exc:
        raise LLMModelNotFoundError(str(exc)) from exc

    api_key = settings.get_llm_api_key(model_name)
    base_url = settings.get_llm_base_url(model_name)
    env_prefix = model_name.replace("-", "_").replace(".", "_").upper()

    if not api_key:
        msg = (
            f"Missing API key for LLM model '{model_name}'. "
            f"Set environment variable LLM_{env_prefix}_API_KEY."
        )
        raise LLMConfigError(msg)

    if not base_url:
        msg = (
            f"Missing base_url for LLM model '{model_name}'. "
            f"Set it in YAML ``llm.models.{model_name}.base_url`` "
            f"or via LLM_{env_prefix}_BASE_URL."
        )
        raise LLMConfigError(msg)

    kwargs: dict[str, Any] = model_cfg.chat_openai_kwargs()
    kwargs["api_key"] = api_key
    kwargs["base_url"] = base_url

    provider = resolve_llm_provider(model_cfg, base_url=base_url)
    if provider == "deepseek":
        client: BaseChatModel = ChatDeepSeek(**kwargs)
    else:
        client = ChatOpenAI(**kwargs)

    logger.info(
        "chat model created name=%s provider=%s model=%s base_url=%s params=%s",
        model_name,
        provider,
        model_cfg.model,
        base_url,
        sorted(k for k in kwargs if k not in {"api_key"}),
    )
    return client


def clear_chat_model_cache() -> None:
    """Clear cached chat model instances (useful in tests)."""
    get_chat_model.cache_clear()
