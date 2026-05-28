from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol

import numpy as np


@dataclass
class Landmark:
    x: float
    y: float
    z: float
    visibility: float


@dataclass
class PoseResult:
    landmarks: Dict[str, Landmark]
    confidence: float
    tracking: bool
    raw_landmarks: List[Landmark]
    raw_result: Optional[object]


class PoseProvider(Protocol):
    def process(self, frame_rgb: np.ndarray) -> PoseResult:
        ...

    def draw_landmarks(self, frame_bgr: np.ndarray, result: PoseResult) -> None:
        ...
