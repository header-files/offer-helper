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
    clear_settings_cache()
