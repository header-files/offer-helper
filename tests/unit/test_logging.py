"""Unit tests for logging context, handlers, and rotation."""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.config import Settings
from app.core.logging import get_logger, get_trace_id, reset_trace_id, set_trace_id
from app.core.logging.formatter import TraceIdFilter
from app.core.logging.setup import configure_logging


def test_trace_id_context_roundtrip() -> None:
    reset_trace_id()
    assert get_trace_id() == "-"
    set_trace_id("abc123")
    assert get_trace_id() == "abc123"
    reset_trace_id()
    assert get_trace_id() == "-"


def test_trace_id_filter_injects_current_context() -> None:
    set_trace_id("trace-filter-1")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    assert TraceIdFilter().filter(record) is True
    assert record.trace_id == "trace-filter-1"
    reset_trace_id()


def test_configure_logging_console_and_rotating_file(tmp_path: Path) -> None:
    log_file = tmp_path / "app.log"
    settings = Settings(
        log_level="INFO",
        log_console_enabled=True,
        log_file_enabled=True,
        log_file_path=str(log_file),
        log_file_max_bytes=1024,
        log_file_backup_count=3,
    )
    configure_logging(settings)

    root = logging.getLogger()
    handler_types = {type(handler).__name__ for handler in root.handlers}
    assert "StreamHandler" in handler_types
    assert "RotatingFileHandler" in handler_types

    set_trace_id("file-trace-1")
    logger = get_logger("offer-helper.test.logging")
    logger.info("console-and-file")
    for handler in root.handlers:
        handler.flush()

    content = log_file.read_text(encoding="utf-8")
    assert "file-trace-1" in content
    assert "console-and-file" in content
    reset_trace_id()


def test_rotating_file_creates_backup_when_full(tmp_path: Path) -> None:
    log_file = tmp_path / "rotate.log"
    settings = Settings(
        log_level="INFO",
        log_console_enabled=False,
        log_file_enabled=True,
        log_file_path=str(log_file),
        log_file_max_bytes=200,
        log_file_backup_count=2,
    )
    configure_logging(settings)
    logger = get_logger("offer-helper.test.rotation")
    set_trace_id("rotate-trace")
    try:
        for index in range(40):
            logger.info("pad-%s-%s", index, "x" * 40)
        for handler in logging.getLogger().handlers:
            handler.flush()
            handler.close()

        assert log_file.exists()
        rotated = tmp_path / "rotate.log.1"
        assert rotated.exists()
    finally:
        reset_trace_id()
        configure_logging(
            Settings(
                log_level="WARNING",
                log_console_enabled=True,
                log_file_enabled=False,
            )
        )
