"""Logging filters and formatters that inject trace_id into every record."""

from __future__ import annotations

import logging

from app.core.logging.context import get_trace_id


class TraceIdFilter(logging.Filter):
    """Ensure every log record carries ``trace_id`` for formatters."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id()
        return True


DEFAULT_LOG_FORMAT = (
    "%(asctime)s %(levelname)s [trace_id=%(trace_id)s] [%(name)s] %(message)s"
)


def build_formatter(fmt: str | None = None) -> logging.Formatter:
    """Build the standard application log formatter."""
    return logging.Formatter(fmt or DEFAULT_LOG_FORMAT)
