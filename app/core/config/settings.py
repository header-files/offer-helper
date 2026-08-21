"""Application settings loaded from YAML config and environment secrets."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.config.llm import LLMModelConfig, LLMSettings

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


def llm_env_prefix(model_name: str) -> str:
    """Build env prefix for a model key, e.g. ``chat`` -> ``LLM_CHAT``."""
    normalized = model_name.strip().replace("-", "_").replace(".", "_").upper()
    return f"LLM_{normalized}"


def _env_value(name: str) -> str:
    """Read a secret/config override from the process environment (config layer only)."""
    return os.environ.get(name, "").strip()


def _parse_llm_settings(raw: dict[str, Any]) -> LLMSettings:
    models_raw = raw.get("models", {})
    models: dict[str, LLMModelConfig] = {}
    if isinstance(models_raw, dict):
        for name, cfg in models_raw.items():
            if isinstance(cfg, dict):
                models[str(name)] = LLMModelConfig.model_validate(cfg)
    default = str(raw.get("default", "chat"))
    return LLMSettings(default=default, models=models)


def _resolve_llm_secrets(
    llm: LLMSettings,
) -> tuple[dict[str, str], dict[str, str]]:
    """
    Resolve per-model API keys / optional base_url overrides from env.

    Convention (no code change when adding a model):
    - ``LLM_<NAME>_API_KEY`` (required at call time)
    - ``LLM_<NAME>_BASE_URL`` (optional; overrides YAML ``base_url``)
    """
    api_keys: dict[str, str] = {}
    base_urls: dict[str, str] = {}
    for name, model_cfg in llm.models.items():
        prefix = llm_env_prefix(name)
        api_keys[name] = _env_value(f"{prefix}_API_KEY")
        env_base = _env_value(f"{prefix}_BASE_URL")
        base_urls[name] = env_base or model_cfg.base_url
    return api_keys, base_urls


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
    log_console_enabled: bool = True
    log_file_enabled: bool = False
    log_file_path: str = "logs/offer-helper.log"
    log_file_max_bytes: int = 10_485_760
    log_file_backup_count: int = 5

    database_url: str = "postgresql+asyncpg://testuser:testpassword@localhost:5432/testdb"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: float = 30.0
    database_pool_recycle: int = 1800
    database_echo: bool = False
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 30
    redis_socket_timeout: float = 5.0
    redis_command_timeout: float = 60.0
    redis_decode_responses: bool = True
    redis_default_ttl: int = 86400

    llm_default: str = "chat"
    llm_models: dict[str, LLMModelConfig] = Field(default_factory=dict)
    llm_api_keys: dict[str, str] = Field(default_factory=dict)
    llm_base_urls: dict[str, str] = Field(default_factory=dict)

    def get_llm_model_config(self, name: str | None = None) -> LLMModelConfig:
        """Return config for a named model (or the default)."""
        model_name = name or self.llm_default
        try:
            return self.llm_models[model_name]
        except KeyError as exc:
            known = ", ".join(sorted(self.llm_models)) or "<none>"
            msg = f"Unknown LLM model '{model_name}'. Known models: {known}"
            raise KeyError(msg) from exc

    def get_llm_api_key(self, name: str | None = None) -> str:
        model_name = name or self.llm_default
        return self.llm_api_keys.get(model_name, "")

    def get_llm_base_url(self, name: str | None = None) -> str:
        model_name = name or self.llm_default
        if model_name in self.llm_base_urls and self.llm_base_urls[model_name]:
            return self.llm_base_urls[model_name]
        return self.get_llm_model_config(model_name).base_url


@lru_cache
def get_settings() -> Settings:
    """Build Settings from YAML + environment variables (secrets)."""
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env", override=False)

    bootstrap = Settings()
    yaml_data = load_yaml_config(bootstrap.app_env)

    app_section = yaml_data.get("app", {})
    server_section = yaml_data.get("server", {})
    logging_section = yaml_data.get("logging", {})
    logging_console = logging_section.get("console", {})
    logging_file = logging_section.get("file", {})
    database_section = yaml_data.get("database", {})
    redis_section = yaml_data.get("redis", {})
    llm_section = yaml_data.get("llm", {})
    llm_settings = _parse_llm_settings(llm_section if isinstance(llm_section, dict) else {})
    llm_api_keys, llm_base_urls = _resolve_llm_secrets(llm_settings)

    merged: dict[str, Any] = {
        "app_name": app_section.get("name", bootstrap.app_name),
        "app_env": app_section.get("env", bootstrap.app_env),
        "debug": app_section.get("debug", bootstrap.debug),
        "api_prefix": app_section.get("api_prefix", bootstrap.api_prefix),
        "host": server_section.get("host", bootstrap.host),
        "port": server_section.get("port", bootstrap.port),
        "log_level": logging_section.get("level", bootstrap.log_level),
        "log_console_enabled": logging_console.get(
            "enabled", bootstrap.log_console_enabled
        ),
        "log_file_enabled": logging_file.get("enabled", bootstrap.log_file_enabled),
        "log_file_path": logging_file.get("path", bootstrap.log_file_path),
        "log_file_max_bytes": logging_file.get(
            "max_bytes", bootstrap.log_file_max_bytes
        ),
        "log_file_backup_count": logging_file.get(
            "backup_count", bootstrap.log_file_backup_count
        ),
        "database_pool_size": database_section.get(
            "pool_size", bootstrap.database_pool_size
        ),
        "database_max_overflow": database_section.get(
            "max_overflow", bootstrap.database_max_overflow
        ),
        "database_pool_timeout": database_section.get(
            "pool_timeout", bootstrap.database_pool_timeout
        ),
        "database_pool_recycle": database_section.get(
            "pool_recycle", bootstrap.database_pool_recycle
        ),
        "database_echo": database_section.get("echo", bootstrap.database_echo),
        "redis_max_connections": redis_section.get(
            "max_connections", bootstrap.redis_max_connections
        ),
        "redis_socket_timeout": redis_section.get(
            "socket_timeout", bootstrap.redis_socket_timeout
        ),
        "redis_command_timeout": redis_section.get(
            "command_timeout", bootstrap.redis_command_timeout
        ),
        "redis_decode_responses": redis_section.get(
            "decode_responses", bootstrap.redis_decode_responses
        ),
        "redis_default_ttl": redis_section.get("default_ttl", bootstrap.redis_default_ttl),
        "llm_default": llm_settings.default,
        "llm_models": llm_settings.models,
        "llm_api_keys": llm_api_keys,
        "llm_base_urls": llm_base_urls,
    }
    return Settings(**merged)


def clear_settings_cache() -> None:
    """Clear cached settings (useful in tests)."""
    get_settings.cache_clear()
    # Avoid stale ChatOpenAI instances bound to previous settings/secrets.
    try:
        from app.infrastructure.llm.factory import clear_chat_model_cache

        clear_chat_model_cache()
    except ImportError:
        return
