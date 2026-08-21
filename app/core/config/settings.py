"""Application settings loaded from YAML config and environment secrets."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnv = Literal["dev", "test", "prod"]

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = PROJECT_ROOT / "config"


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override into base and return a new dict."""
    result: dict[str, Any] = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        msg = f"Config file must be a mapping: {path}"
        raise ValueError(msg)
    return data


def load_yaml_config(app_env: AppEnv) -> dict[str, Any]:
    """Load base.yaml and merge with environment-specific YAML."""
    base = _load_yaml(CONFIG_DIR / "base.yaml")
    env_config = _load_yaml(CONFIG_DIR / f"{app_env}.yaml")
    return _deep_merge(base, env_config)


class Settings(BaseSettings):
    """Unified application settings. Business code must use this, not os.getenv()."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "offer-helper"
    app_env: AppEnv = "dev"
    debug: bool = False
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://offer:offer@postgres:5432/offer_helper"
    redis_url: str = "redis://redis:6379/0"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""


@lru_cache
def get_settings() -> Settings:
    """Build Settings from YAML + environment variables (secrets)."""
    bootstrap = Settings()
    yaml_data = load_yaml_config(bootstrap.app_env)

    app_section = yaml_data.get("app", {})
    server_section = yaml_data.get("server", {})
    logging_section = yaml_data.get("logging", {})

    merged: dict[str, Any] = {
        "app_name": app_section.get("name", bootstrap.app_name),
        "app_env": app_section.get("env", bootstrap.app_env),
        "debug": app_section.get("debug", bootstrap.debug),
        "api_prefix": app_section.get("api_prefix", bootstrap.api_prefix),
        "host": server_section.get("host", bootstrap.host),
        "port": server_section.get("port", bootstrap.port),
        "log_level": logging_section.get("level", bootstrap.log_level),
    }
    # Secrets stay env-driven; re-instantiate so env vars still apply for DB/Redis/LLM.
    return Settings(**merged)


def clear_settings_cache() -> None:
    """Clear cached settings (useful in tests)."""
    get_settings.cache_clear()
