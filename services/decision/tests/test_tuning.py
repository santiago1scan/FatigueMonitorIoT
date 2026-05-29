from __future__ import annotations

from app.biomechanics.features import BiomechFeatures
from app.biomechanics.tuning import ThresholdTuner
from app.config.settings import Settings
from app.state_machine.states import BiomechState


def _features(knee: float, velocity: float) -> BiomechFeatures:
    return BiomechFeatures(
        knee_angle_avg=knee,
        hip_angle_avg=None,
        knee_asymmetry=None,
        back_inclination=0.0,
        velocity_vertical=velocity,
        depth_score=1.0,
        stability=1.0,
        consistency=1.0,
    )


def test_tuning_suggestions_require_samples() -> None:
    settings = Settings(tuning_min_samples=2, tuning_window_size=10)
    tuner = ThresholdTuner(settings)

    tuner.update(BiomechState.STANDING, _features(175.0, 0.0))
    assert tuner.suggestions() is None

    tuner.update(BiomechState.STANDING, _features(172.0, 0.0))
    tuner.update(BiomechState.BOTTOM, _features(95.0, 0.0))
    tuner.update(BiomechState.BOTTOM, _features(100.0, 0.0))
    tuner.update(BiomechState.DESCENDING, _features(130.0, -0.2))
    tuner.update(BiomechState.ASCENDING, _features(130.0, 0.3))

    suggestions = tuner.suggestions()
    assert suggestions is not None
    assert suggestions.standing_knee_angle_min is not None
    assert suggestions.bottom_knee_angle_max is not None
