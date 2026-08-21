"""Unit tests for multi-model chat factory."""

from __future__ import annotations

from typing import Any

import pytest
from langchain_deepseek import ChatDeepSeek

from app.core.config import clear_settings_cache, get_settings, llm_env_prefix
from app.core.config.llm import LLMModelConfig
from app.core.exceptions import LLMConfigError, LLMModelNotFoundError
from app.infrastructure.llm import get_chat_model, resolve_llm_provider


@pytest.fixture(autouse=True)
def _reset_settings(monkeypatch: Any) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LLM_CHAT_API_KEY", "sk-chat-test")
    monkeypatch.setenv("LLM_REASONER_API_KEY", "sk-reasoner-test")
    clear_settings_cache()
    yield
    clear_settings_cache()


def test_llm_env_prefix() -> None:
    assert llm_env_prefix("chat") == "LLM_CHAT"
    assert llm_env_prefix("my-model") == "LLM_MY_MODEL"


def test_resolve_llm_provider_auto_deepseek_by_model() -> None:
    cfg = LLMModelConfig.model_validate(
        {"model": "deepseek-v4-flash", "base_url": "https://example.com"}
    )
    assert resolve_llm_provider(cfg) == "deepseek"


def test_resolve_llm_provider_auto_openai() -> None:
    cfg = LLMModelConfig.model_validate(
        {"model": "gpt-4o-mini", "base_url": "https://api.openai.com/v1"}
    )
    assert resolve_llm_provider(cfg) == "openai"


def test_resolve_llm_provider_explicit_override() -> None:
    cfg = LLMModelConfig.model_validate(
        {
            "model": "custom-model",
            "base_url": "https://proxy.example.com/v1",
            "provider": "deepseek",
        }
    )
    assert resolve_llm_provider(cfg) == "deepseek"


def test_get_chat_model_unknown_raises() -> None:
    with pytest.raises(LLMModelNotFoundError):
        get_chat_model("does-not-exist")


def test_get_chat_model_missing_api_key_raises(monkeypatch: Any) -> None:
    monkeypatch.setenv("LLM_CHAT_API_KEY", "")
    clear_settings_cache()
    with pytest.raises(LLMConfigError, match="LLM_CHAT_API_KEY"):
        get_chat_model("chat")


def test_base_url_env_override(monkeypatch: Any) -> None:
    monkeypatch.setenv("LLM_CHAT_BASE_URL", "https://custom.example.com/v1")
    clear_settings_cache()
    settings = get_settings()
    assert settings.get_llm_base_url("chat") == "https://custom.example.com/v1"
    client = get_chat_model("chat")
    assert "custom.example.com" in str(client.openai_api_base)


def test_llm_model_config_excludes_provider_from_client_kwargs() -> None:
    cfg = LLMModelConfig.model_validate(
        {
            "model": "gpt-test",
            "base_url": "https://example.com/v1",
            "provider": "openai",
            "temperature": 0.1,
            "timeout": 15,
            "max_retries": 1,
            "top_p": 0.9,
            "presence_penalty": 0.5,
            "streaming": True,
        }
    )
    kwargs = cfg.chat_openai_kwargs()
    assert kwargs["model"] == "gpt-test"
    assert "base_url" not in kwargs
    assert "provider" not in kwargs
    assert kwargs["temperature"] == 0.1
    assert kwargs["top_p"] == 0.9
    assert kwargs["presence_penalty"] == 0.5
    assert kwargs["streaming"] is True
