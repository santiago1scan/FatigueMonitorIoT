from __future__ import annotations

from app.biomechanics.features import BiomechFeatures
from app.config.settings import Settings
from app.state_machine.machine import StateUpdate
from app.state_machine.repetition import RepCounter
from app.state_machine.states import BiomechState


def _features(depth_score: float) -> BiomechFeatures:
    return BiomechFeatures(
        knee_angle_avg=0.0,
        hip_angle_avg=None,
        knee_asymmetry=None,
        back_inclination=0.0,
        velocity_vertical=0.0,
        depth_score=depth_score,
        stability=1.0,
        consistency=1.0,
    )


def _update(state: BiomechState) -> StateUpdate:
    return StateUpdate(
        state=state,
        previous_state=state,
        changed=True,
        confidence=1.0,
    )


def test_rep_sequence_counts_once() -> None:
    settings = Settings(min_rep_interval_s=0.0, depth_score_min=0.8)
    counter = RepCounter(settings)

    assert counter.update(_update(BiomechState.DESCENDING), _features(0.9)) is None
    assert counter.update(_update(BiomechState.BOTTOM), _features(0.9)) is None
    assert counter.update(_update(BiomechState.ASCENDING), _features(0.9)) is None
    event = counter.update(_update(BiomechState.LOCKOUT), _features(0.9))

    assert event is not None
    assert event.rep_count == 1
    assert event.depth_ok is True


def test_rep_sequence_depth_fails() -> None:
    settings = Settings(min_rep_interval_s=0.0, depth_score_min=0.8)
    counter = RepCounter(settings)

    counter.update(_update(BiomechState.DESCENDING), _features(0.4))
    counter.update(_update(BiomechState.BOTTOM), _features(0.4))
    counter.update(_update(BiomechState.ASCENDING), _features(0.4))
    event = counter.update(_update(BiomechState.LOCKOUT), _features(0.4))

    assert event is not None
    assert event.depth_ok is False
