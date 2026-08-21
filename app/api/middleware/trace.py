"""HTTP middleware that binds a trace_id for the full request lifecycle."""

from __future__ import annotations

import time
import uuid

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging.context import reset_trace_id, set_trace_id
from app.core.logging.setup import get_logger

logger = get_logger(__name__)

TRACE_ID_HEADER = "X-Trace-Id"
REQUEST_ID_HEADER = "X-Request-Id"


def _extract_or_create_trace_id(headers: Headers) -> str:
    incoming = headers.get(TRACE_ID_HEADER) or headers.get(REQUEST_ID_HEADER)
    if incoming and incoming.strip():
        return incoming.strip()
    return uuid.uuid4().hex


class TraceIdMiddleware:
    """
    Pure ASGI middleware so contextvars propagate through the request.

    ``BaseHTTPMiddleware`` runs the app in a child task and can drop contextvars;
    this implementation keeps ``trace_id`` visible to handlers, services, and logs.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        trace_id = _extract_or_create_trace_id(headers)
        set_trace_id(trace_id)

        method = scope.get("method", "")
        path = scope.get("path", "")
        started = time.perf_counter()
        status_code = 500

        logger.info("request started method=%s path=%s", method, path)

        async def send_with_trace_id(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message.get("status", 500))
                response_headers = MutableHeaders(scope=message)
                response_headers[TRACE_ID_HEADER] = trace_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_trace_id)
        except Exception:
            elapsed_ms = (time.perf_counter() - started) * 1000
            logger.exception(
                "request failed method=%s path=%s duration_ms=%.2f",
                method,
                path,
                elapsed_ms,
            )
            raise
        else:
            elapsed_ms = (time.perf_counter() - started) * 1000
            logger.info(
                "request finished method=%s path=%s status=%s duration_ms=%.2f",
                method,
                path,
                status_code,
                elapsed_ms,
            )
        finally:
            reset_trace_id()
