"""Unit tests for settings loading."""

from typing import Any

from app.core.config import clear_settings_cache, get_settings, load_yaml_config


def test_load_yaml_config_merges_base_and_env() -> None:
    config = load_yaml_config("test")
    assert config["app"]["name"] == "offer-helper"
    assert config["app"]["env"] == "test"
    assert config["logging"]["level"] == "WARNING"


def test_get_settings_reads_yaml(monkeypatch: Any) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    clear_settings_cache()
    settings = get_settings()
    assert settings.app_name == "offer-helper"
    assert settings.app_env == "test"
    assert settings.debug is True
    assert settings.redis_max_connections == 30
    assert settings.redis_decode_responses is True
    assert settings.log_console_enabled is True
    assert settings.log_file_enabled is False
    assert settings.database_pool_size == 5
    assert settings.database_echo is False
    assert settings.llm_default == "chat"
    assert "chat" in settings.llm_models
    assert "reasoner" in settings.llm_models
    clear_settings_cache()
