"""Health check schemas."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response payload for GET /health."""

    status: str = Field(default="ok", examples=["ok"])
