from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import math

from app.providers.base import Landmark


@dataclass
class BiomechanicsMetrics:
    angles: Dict[str, Optional[float]]
    back_inclination: Optional[float]
    torso_leg_ratio: Optional[float]
    vertical_velocity: Optional[float]
    joint_positions: Dict[str, Dict[str, float]]


class BiomechanicsCalculator:
    def __init__(self) -> None:
        self._prev_hip_y: Optional[float] = None
        self._prev_time: Optional[float] = None

    def compute(
        self, landmarks: Dict[str, Landmark], timestamp: float
    ) -> BiomechanicsMetrics:
        angles = {
            "left_knee": self._angle(
                landmarks.get("left_hip"),
                landmarks.get("left_knee"),
                landmarks.get("left_ankle"),
            ),
            "right_knee": self._angle(
                landmarks.get("right_hip"),
                landmarks.get("right_knee"),
                landmarks.get("right_ankle"),
            ),
            "left_hip": self._angle(
                landmarks.get("left_shoulder"),
                landmarks.get("left_hip"),
                landmarks.get("left_knee"),
            ),
            "right_hip": self._angle(
                landmarks.get("right_shoulder"),
                landmarks.get("right_hip"),
                landmarks.get("right_knee"),
            ),
        }

        back_inclination = self._back_inclination(landmarks)
        torso_leg_ratio = self._torso_leg_ratio(landmarks)
        vertical_velocity = self._vertical_velocity(landmarks, timestamp)
        joint_positions = self._positions(landmarks)

        return BiomechanicsMetrics(
            angles=angles,
            back_inclination=back_inclination,
            torso_leg_ratio=torso_leg_ratio,
            vertical_velocity=vertical_velocity,
            joint_positions=joint_positions,
        )

    def _angle(
        self,
        a: Optional[Landmark],
        b: Optional[Landmark],
        c: Optional[Landmark],
    ) -> Optional[float]:
        if a is None or b is None or c is None:
            return None
        ab = (a.x - b.x, a.y - b.y)
        cb = (c.x - b.x, c.y - b.y)
        ab_norm = math.hypot(*ab)
        cb_norm = math.hypot(*cb)
        if ab_norm == 0 or cb_norm == 0:
            return None
        dot = ab[0] * cb[0] + ab[1] * cb[1]
        cos_theta = max(min(dot / (ab_norm * cb_norm), 1.0), -1.0)
        return math.degrees(math.acos(cos_theta))

    def _back_inclination(self, landmarks: Dict[str, Landmark]) -> Optional[float]:
        shoulder = self._midpoint(
            landmarks.get("left_shoulder"), landmarks.get("right_shoulder")
        )
        hip = self._midpoint(landmarks.get("left_hip"), landmarks.get("right_hip"))
        if shoulder is None or hip is None:
            return None
        vec = (shoulder[0] - hip[0], shoulder[1] - hip[1])
        norm = math.hypot(*vec)
        if norm == 0:
            return None
        vertical = (0.0, -1.0)
        dot = vec[0] * vertical[0] + vec[1] * vertical[1]
        cos_theta = max(min(dot / norm, 1.0), -1.0)
        return math.degrees(math.acos(cos_theta))

    def _torso_leg_ratio(self, landmarks: Dict[str, Landmark]) -> Optional[float]:
        shoulder = self._midpoint(
            landmarks.get("left_shoulder"), landmarks.get("right_shoulder")
        )
        hip = self._midpoint(landmarks.get("left_hip"), landmarks.get("right_hip"))
        ankle = self._midpoint(
            landmarks.get("left_ankle"), landmarks.get("right_ankle")
        )
        if shoulder is None or hip is None or ankle is None:
            return None
        torso = math.hypot(shoulder[0] - hip[0], shoulder[1] - hip[1])
        leg = math.hypot(ankle[0] - hip[0], ankle[1] - hip[1])
        if leg == 0:
            return None
        return torso / leg

    def _vertical_velocity(
        self, landmarks: Dict[str, Landmark], timestamp: float
    ) -> Optional[float]:
        hip = self._midpoint(landmarks.get("left_hip"), landmarks.get("right_hip"))
        if hip is None:
            return None
        hip_y = hip[1]
        if self._prev_hip_y is None or self._prev_time is None:
            self._prev_hip_y = hip_y
            self._prev_time = timestamp
            return None
        dt = timestamp - self._prev_time
        if dt <= 0:
            return None
        velocity = (hip_y - self._prev_hip_y) / dt
        self._prev_hip_y = hip_y
        self._prev_time = timestamp
        return velocity

    def _midpoint(
        self, left: Optional[Landmark], right: Optional[Landmark]
    ) -> Optional[Tuple[float, float]]:
        if left is None or right is None:
            return None
        return ((left.x + right.x) / 2.0, (left.y + right.y) / 2.0)

    def _positions(self, landmarks: Dict[str, Landmark]) -> Dict[str, Dict[str, float]]:
        positions: Dict[str, Dict[str, float]] = {}
        for name, lm in landmarks.items():
            positions[name] = {"x": lm.x, "y": lm.y, "z": lm.z}
        return positions
