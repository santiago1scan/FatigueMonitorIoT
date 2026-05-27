from __future__ import annotations

from pydantic import BaseModel, Field


class AssistActivatePayload(BaseModel):
    force: float = Field(ge=0.0, le=1.0)
    request_id: str | None = None


class AssistDisablePayload(BaseModel):
    request_id: str | None = None
