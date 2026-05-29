from __future__ import annotations

from typing import Dict

from app.biomechanics.types import PoseFrame, SmoothedFrame
from app.config.settings import Settings


class EmaFilter:
    def __init__(self, alpha: float) -> None:
        self._alpha = alpha
        self._value: float | None = None

    def update(self, value: float | None) -> float | None:
        if value is None:
            return self._value
        if self._value is None:
            self._value = value
        else:
            self._value = (self._alpha * value) + ((1.0 - self._alpha) * self._value)
        return self._value


class EmaSmoother:
    def __init__(self, settings: Settings) -> None:
        self._angle_filters: Dict[str, EmaFilter] = {}
        self._angles_alpha = settings.smoothing_alpha_angles
        self._velocity_filter = EmaFilter(settings.smoothing_alpha_velocity)
        self._back_filter = EmaFilter(settings.smoothing_alpha_back)

    def update(self, frame: PoseFrame) -> SmoothedFrame:
        angles: Dict[str, float] = {}
        for key, value in frame.angles.items():
            if value is None:
                continue
            filt = self._angle_filters.setdefault(key, EmaFilter(self._angles_alpha))
            filtered = filt.update(float(value))
            if filtered is not None:
                angles[key] = filtered

        return SmoothedFrame(
            timestamp=frame.timestamp,
            received_time=frame.received_time,
            tracking=frame.tracking,
            confidence=frame.confidence,
            angles=angles,
            back_inclination=self._back_filter.update(frame.back_inclination) or 0.0,
            velocity_vertical=self._velocity_filter.update(frame.velocity_vertical) or 0.0,
            positions=frame.positions,
            torso_leg_ratio=frame.torso_leg_ratio,
        )
