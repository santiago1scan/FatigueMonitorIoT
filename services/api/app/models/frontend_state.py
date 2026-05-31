from pydantic import BaseModel
from app.models.fatigue import FatigueEvent
from typing import Dict


class FatigueFlags(BaseModel):
    green: bool
    yellow: bool
    red: bool


class FrontendState(BaseModel):
    repetitions: int
    fatigue_score: float
    fatigue: FatigueFlags
    play_sound: bool
    active: bool

