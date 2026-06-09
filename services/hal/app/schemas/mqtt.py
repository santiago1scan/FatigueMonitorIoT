from __future__ import annotations

from pydantic import BaseModel


class AssistDisablePayload(BaseModel):
    request_id: str | None = None


class FailureEventPayload(BaseModel):
    timestamp: str
    event: str
    confidence: float | None = None
