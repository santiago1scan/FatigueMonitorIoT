from __future__ import annotations

from app.biomechanics.features import BiomechFeatures
from app.biomechanics.types import SmoothedFrame
from app.config.settings import Settings
from app.state_machine.machine import BiomechStateMachine
from app.state_machine.states import BiomechState


def _features(knee: float | None, velocity: float) -> BiomechFeatures:
    return BiomechFeatures(
        knee_angle_avg=knee,
        hip_angle_avg=None,
        knee_asymmetry=None,
        back_inclination=0.0,
        velocity_vertical=velocity,
        depth_score=0.0,
        stability=1.0,
        consistency=1.0,
    )


def _frame(confidence: float = 1.0, tracking: bool = True) -> SmoothedFrame:
    return SmoothedFrame(
        timestamp="2026-05-28T00:00:00Z",
        received_time=0.0,
        tracking=tracking,
        confidence=confidence,
        angles={},
        back_inclination=0.0,
        velocity_vertical=0.0,
        positions={},
        torso_leg_ratio=None,
    )


def test_state_requires_confirm_frames() -> None:
    settings = Settings(min_confirm_frames=2)
    machine = BiomechStateMachine(settings)

    features = _features(settings.standing_knee_angle_min + 1.0, 0.0)
    frame = _frame()

    update = machine.update(features, frame)
    assert update.state == BiomechState.IDLE

    update = machine.update(features, frame)
    assert update.state == BiomechState.STANDING


def test_tracking_lost_overrides_state() -> None:
    settings = Settings(min_confirm_frames=1, min_confidence_lost=0.4)
    machine = BiomechStateMachine(settings)
    features = _features(settings.standing_knee_angle_min + 1.0, 0.0)

    update = machine.update(features, _frame(confidence=0.2))
    assert update.state == BiomechState.TRACKING_LOST
