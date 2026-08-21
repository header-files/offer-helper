"""Application logging configuration: console + rotating file."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import Settings, get_settings
from app.core.config.settings import PROJECT_ROOT
from app.core.logging.formatter import DEFAULT_LOG_FORMAT, TraceIdFilter, build_formatter

_CONFIGURED = False


def _resolve_log_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def configure_logging(settings: Settings | None = None) -> None:
    """
    Configure root logger handlers from Settings.

    Idempotent: clearing existing handlers avoids duplicates across reloads/tests.
    """
    global _CONFIGURED
    cfg = settings or get_settings()
    level = getattr(logging, cfg.log_level.upper(), logging.INFO)
    formatter = build_formatter(DEFAULT_LOG_FORMAT)
    trace_filter = TraceIdFilter()

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    if cfg.log_console_enabled:
        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(formatter)
        console.addFilter(trace_filter)
        root.addHandler(console)

    if cfg.log_file_enabled:
        log_path = _resolve_log_path(cfg.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            filename=log_path,
            maxBytes=cfg.log_file_max_bytes,
            backupCount=cfg.log_file_backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(trace_filter)
        root.addHandler(file_handler)

    # Keep uvicorn/access logs on the same handlers so they also carry trace_id
    # when emitted inside a request context.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        named = logging.getLogger(name)
        named.handlers.clear()
        named.propagate = True

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Business code must not configure logging ad hoc."""
    return logging.getLogger(name)


def is_logging_configured() -> bool:
    """Whether configure_logging has been applied at least once."""
    return _CONFIGURED
