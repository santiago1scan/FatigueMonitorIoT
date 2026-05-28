from __future__ import annotations

from typing import Dict, Optional


def build_pose_event(
    timestamp: str,
    tracking: bool,
    landmarks: Dict[str, Dict[str, float]],
    confidence: float,
    inference_ms: float,
) -> dict:
    return {
        "timestamp": timestamp,
        "tracking": tracking,
        "landmarks": landmarks,
        "confidence": confidence,
        "inference_ms": inference_ms,
    }


def build_metrics_event(
    timestamp: str,
    tracking: bool,
    angles: Dict[str, Optional[float]],
    back_inclination: Optional[float],
    torso_leg_ratio: Optional[float],
    vertical_velocity: Optional[float],
    joint_positions: Dict[str, Dict[str, float]],
) -> dict:
    return {
        "timestamp": timestamp,
        "tracking": tracking,
        "angles": angles,
        "back_inclination": back_inclination,
        "torso_leg_ratio": torso_leg_ratio,
        "velocity": {"vertical": vertical_velocity},
        "positions": joint_positions,
    }


def build_health_event(timestamp: str, metrics: dict) -> dict:
    payload = {"timestamp": timestamp}
    payload.update(metrics)
    return payload
