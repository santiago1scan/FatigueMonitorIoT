from pydantic import BaseModel


class FatigueEvent(BaseModel):
    timestamp: str
    fatigue_score: float
