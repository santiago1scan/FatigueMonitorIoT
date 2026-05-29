from __future__ import annotations

from app.biomechanics.features import BiomechFeatures
from app.config.settings import Settings
from app.fatigue.estimator import FatigueEstimator
from app.state_machine.machine import StateUpdate
from app.state_machine.repetition import RepEvent
from app.state_machine.states import BiomechState


def _features(velocity: float, back: float, asym: float, stability: float) -> BiomechFeatures:
    return BiomechFeatures(
        knee_angle_avg=120.0,
        hip_angle_avg=90.0,
        knee_asymmetry=asym,
        back_inclination=back,
        velocity_vertical=velocity,
        depth_score=1.0,
        stability=stability,
        consistency=1.0,
    )


def _update(state: BiomechState) -> StateUpdate:
    return StateUpdate(
        state=state,
        previous_state=state,
        changed=True,
        confidence=1.0,
    )


def _rep_event(rep: int) -> RepEvent:
    return RepEvent(rep_count=rep, depth_ok=True)


def test_fatigue_increases_after_baseline() -> None:
    settings = Settings(baseline_reps=2)
    estimator = FatigueEstimator(settings)

    for rep in range(2):
        estimator.update(_features(0.4, 5.0, 2.0, 0.9), _update(BiomechState.ASCENDING), None)
        estimator.update(_features(0.4, 5.0, 2.0, 0.9), _update(BiomechState.ASCENDING), _rep_event(rep))

    score = estimator.update(
        _features(0.1, 12.0, 6.0, 0.6),
        _update(BiomechState.ASCENDING),
        _rep_event(3),
    )

    assert score > 0.0
