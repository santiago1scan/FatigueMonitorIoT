from pydantic import BaseModel
from typing import Optional


class StateSnapshot(BaseModel):
    timestamp: Optional[str]
    tracking: Optional[bool]
    details: dict = {}
