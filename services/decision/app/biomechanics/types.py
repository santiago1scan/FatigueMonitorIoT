from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class PoseFrame:
    timestamp: str
    received_time: float
    tracking: bool
    confidence: float
    angles: Dict[str, float]
    back_inclination: float
    velocity_vertical: float
    positions: Dict[str, Dict[str, float]]
    torso_leg_ratio: float | None = None


@dataclass
class SmoothedFrame:
    timestamp: str
    received_time: float
    tracking: bool
    confidence: float
    angles: Dict[str, float]
    back_inclination: float
    velocity_vertical: float
    positions: Dict[str, Dict[str, float]]
    torso_leg_ratio: float | None = None
