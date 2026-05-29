from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.biomechanics.types import SmoothedFrame
from app.buffers.pose_buffer import PoseBuffer
from app.config.settings import Settings
from app.utils.math import clamp, mean, safe_div, std


@dataclass
class BiomechFeatures:
    knee_angle_avg: float | None
    hip_angle_avg: float | None
    knee_asymmetry: float | None
    back_inclination: float
    velocity_vertical: float
    depth_score: float
    stability: float
    consistency: float


def _angle(frame: SmoothedFrame, key: str) -> float | None:
    value = frame.angles.get(key)
    if value is None:
        return None
    return float(value)


def _series(buffer: PoseBuffer, key: str) -> List[float]:
    values: List[float] = []
    for item in buffer.frames:
        angle = item.angles.get(key)
        if angle is None:
            continue
        values.append(float(angle))
    return values


def compute_features(
    frame: SmoothedFrame,
    buffer: PoseBuffer,
    settings: Settings,
) -> BiomechFeatures:
    left_knee = _angle(frame, "left_knee")
    right_knee = _angle(frame, "right_knee")
    left_hip = _angle(frame, "left_hip")
    right_hip = _angle(frame, "right_hip")

    knee_angle_avg = mean(v for v in (left_knee, right_knee) if v is not None)
    hip_angle_avg = mean(v for v in (left_hip, right_hip) if v is not None)
    knee_asymmetry = None
    if left_knee is not None and right_knee is not None:
        knee_asymmetry = abs(left_knee - right_knee)

    depth_score = 0.0
    if knee_angle_avg is not None:
        denom = max(1.0, settings.standing_knee_angle_min - settings.bottom_knee_angle_max)
        depth_score = clamp(
            (settings.standing_knee_angle_min - knee_angle_avg) / denom,
            0.0,
            1.0,
        )

    knee_series = _series(buffer, "left_knee") + _series(buffer, "right_knee")
    stability_std = std(knee_series)
    stability = 1.0
    if stability_std is not None:
        stability = 1.0 - clamp(stability_std / settings.stability_std_max, 0.0, 1.0)

    mean_knee = mean(knee_series) or 0.0
    cv = 0.0
    if stability_std is not None:
        cv = safe_div(stability_std, mean_knee, 0.0)
    consistency = 1.0 - clamp(cv / settings.consistency_cv_max, 0.0, 1.0)

    return BiomechFeatures(
        knee_angle_avg=knee_angle_avg,
        hip_angle_avg=hip_angle_avg,
        knee_asymmetry=knee_asymmetry,
        back_inclination=frame.back_inclination,
        velocity_vertical=frame.velocity_vertical,
        depth_score=depth_score,
        stability=stability,
        consistency=consistency,
    )
