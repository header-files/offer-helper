"""Request-scoped trace id using contextvars."""

from __future__ import annotations

from contextvars import ContextVar

_TRACE_ID: ContextVar[str] = ContextVar("trace_id", default="-")


def get_trace_id() -> str:
    """Return the current request trace id, or ``-`` when outside a request."""
    return _TRACE_ID.get()


def set_trace_id(trace_id: str) -> None:
    """Bind a trace id to the current async/task context."""
    _TRACE_ID.set(trace_id)


def reset_trace_id() -> None:
    """Clear the trace id after a request finishes."""
    _TRACE_ID.set("-")
