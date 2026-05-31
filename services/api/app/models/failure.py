from pydantic import BaseModel
from typing import Optional


class FailureEvent(BaseModel):
    timestamp: str
    event: str
    confidence: Optional[float] = None
