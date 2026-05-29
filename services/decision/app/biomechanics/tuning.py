from __future__ import annotations

from dataclasses import dataclass
from math import ceil, floor
from typing import Dict, List

from app.biomechanics.features import BiomechFeatures
from app.config.settings import Settings
from app.state_machine.states import BiomechState


def _percentile(values: List[float], q: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    index = (len(values) - 1) * q
    low = floor(index)
    high = ceil(index)
    if low == high:
        return values[int(index)]
    weight = index - low
    return values[low] * (1.0 - weight) + values[high] * weight


@dataclass
class TuningSuggestions:
    standing_knee_angle_min: float | None
    bottom_knee_angle_max: float | None
    vel_descend_threshold: float | None
    vel_ascend_threshold: float | None
    samples: Dict[str, int]


class ThresholdTuner:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._standing_angles: List[float] = []
        self._bottom_angles: List[float] = []
        self._desc_velocities: List[float] = []
        self._asc_velocities: List[float] = []

    def update(self, state: BiomechState, features: BiomechFeatures) -> None:
        if not self._settings.tuning_enabled:
            return

        if features.knee_angle_avg is not None:
            if state in (BiomechState.STANDING, BiomechState.LOCKOUT):
                self._append(self._standing_angles, features.knee_angle_avg)
            if state == BiomechState.BOTTOM:
                self._append(self._bottom_angles, features.knee_angle_avg)

        if state == BiomechState.DESCENDING and features.velocity_vertical < 0:
            self._append(self._desc_velocities, features.velocity_vertical)
        if state == BiomechState.ASCENDING and features.velocity_vertical > 0:
            self._append(self._asc_velocities, features.velocity_vertical)

    def suggestions(self) -> TuningSuggestions | None:
        if not self._settings.tuning_enabled:
            return None

        if (
            len(self._standing_angles) < self._settings.tuning_min_samples
            or len(self._bottom_angles) < self._settings.tuning_min_samples
        ):
            return None

        standing_knee = _percentile(self._standing_angles, 0.1)
        bottom_knee = _percentile(self._bottom_angles, 0.9)
        desc_vel = _percentile(self._desc_velocities, 0.7)
        asc_vel = _percentile(self._asc_velocities, 0.3)

        return TuningSuggestions(
            standing_knee_angle_min=standing_knee,
            bottom_knee_angle_max=bottom_knee,
            vel_descend_threshold=desc_vel,
            vel_ascend_threshold=asc_vel,
            samples={
                "standing": len(self._standing_angles),
                "bottom": len(self._bottom_angles),
                "descending": len(self._desc_velocities),
                "ascending": len(self._asc_velocities),
            },
        )

    def _append(self, bucket: List[float], value: float) -> None:
        bucket.append(value)
        if len(bucket) > self._settings.tuning_window_size:
            bucket.pop(0)
