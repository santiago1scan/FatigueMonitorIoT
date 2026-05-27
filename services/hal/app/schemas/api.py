from __future__ import annotations

from pydantic import BaseModel, Field


class ServoTestRequest(BaseModel):
    angle: float | None = Field(default=None, ge=0.0, le=180.0)
    force: float | None = Field(default=None, ge=0.0, le=1.0)
