"""API tests for health endpoint and request tracing."""

from fastapi.testclient import TestClient

from app.api.middleware import TRACE_ID_HEADER
from app.main import create_app


def test_health_returns_ok() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers.get(TRACE_ID_HEADER)


def test_health_preserves_incoming_trace_id() -> None:
    client = TestClient(create_app())
    response = client.get("/health", headers={TRACE_ID_HEADER: "client-trace-xyz"})
    assert response.status_code == 200
    assert response.headers.get(TRACE_ID_HEADER) == "client-trace-xyz"


def test_health_accepts_x_request_id_as_trace_id() -> None:
    client = TestClient(create_app())
    response = client.get("/health", headers={"X-Request-Id": "req-123"})
    assert response.status_code == 200
    assert response.headers.get(TRACE_ID_HEADER) == "req-123"
