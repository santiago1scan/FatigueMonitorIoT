from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.biomechanics.features import BiomechFeatures
from app.config.settings import Settings
from app.smoothing.ema import EmaFilter
from app.state_machine.machine import StateUpdate
from app.state_machine.repetition import RepEvent
from app.state_machine.states import BiomechState
from app.utils.math import clamp, mean, safe_div


@dataclass
class RepMetrics:
    asc_velocity_avg: float
    back_inclination_max: float
    asymmetry_avg: float
    stability_avg: float


class _RepAccumulator:
    def __init__(self) -> None:
        self._asc_velocities: List[float] = []
        self._back_max = 0.0
        self._asymmetry: List[float] = []
        self._stability: List[float] = []

    def update(self, features: BiomechFeatures) -> None:
        if features.velocity_vertical > 0:
            self._asc_velocities.append(features.velocity_vertical)
        if features.back_inclination > self._back_max:
            self._back_max = features.back_inclination
        if features.knee_asymmetry is not None:
            self._asymmetry.append(features.knee_asymmetry)
        self._stability.append(features.stability)

    def finalize(self) -> RepMetrics | None:
        asc_velocity_avg = mean(self._asc_velocities)
        stability_avg = mean(self._stability)
        if asc_velocity_avg is None or stability_avg is None:
            return None
        return RepMetrics(
            asc_velocity_avg=asc_velocity_avg,
            back_inclination_max=self._back_max,
            asymmetry_avg=mean(self._asymmetry) or 0.0,
            stability_avg=stability_avg,
        )

    def reset(self) -> None:
        self._asc_velocities.clear()
        self._back_max = 0.0
        self._asymmetry.clear()
        self._stability.clear()


class FatigueEstimator:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._baseline_reps: List[RepMetrics] = []
        self._baseline: RepMetrics | None = None
        self._score_filter = EmaFilter(settings.fatigue_score_smoothing)
        self._current_score = 0.0
        self._rep_acc = _RepAccumulator()

    def update(
        self,
        features: BiomechFeatures,
        state_update: StateUpdate,
        rep_event: RepEvent | None,
    ) -> float:
        if state_update.state in (
            BiomechState.DESCENDING,
            BiomechState.BOTTOM,
            BiomechState.ASCENDING,
        ):
            self._rep_acc.update(features)

        if rep_event:
            rep_metrics = self._rep_acc.finalize()
            self._rep_acc.reset()
            if rep_metrics:
                self._update_baseline_or_score(rep_metrics)

        return self._current_score

    def _update_baseline_or_score(self, metrics: RepMetrics) -> None:
        if self._baseline is None:
            self._baseline_reps.append(metrics)
            if len(self._baseline_reps) >= self._settings.baseline_reps:
                self._baseline = self._average_rep_metrics(self._baseline_reps)
            return

        raw_score = self._compute_score(metrics, self._baseline)
        smoothed = self._score_filter.update(raw_score)
        self._current_score = smoothed if smoothed is not None else raw_score

    def _average_rep_metrics(self, reps: List[RepMetrics]) -> RepMetrics:
        return RepMetrics(
            asc_velocity_avg=mean(r.asc_velocity_avg for r in reps) or 0.0,
            back_inclination_max=mean(r.back_inclination_max for r in reps) or 0.0,
            asymmetry_avg=mean(r.asymmetry_avg for r in reps) or 0.0,
            stability_avg=mean(r.stability_avg for r in reps) or 0.0,
        )

    def _compute_score(self, metrics: RepMetrics, baseline: RepMetrics) -> float:
        vel_drop = clamp(
            safe_div(baseline.asc_velocity_avg - metrics.asc_velocity_avg, baseline.asc_velocity_avg, 0.0),
            0.0,
            1.0,
        )
        back_increase = clamp(
            safe_div(metrics.back_inclination_max - baseline.back_inclination_max, baseline.back_inclination_max, 0.0),
            0.0,
            1.0,
        )
        asym_increase = clamp(
            safe_div(metrics.asymmetry_avg - baseline.asymmetry_avg, baseline.asymmetry_avg, 0.0),
            0.0,
            1.0,
        )
        stability_drop = clamp(
            safe_div(baseline.stability_avg - metrics.stability_avg, baseline.stability_avg, 0.0),
            0.0,
            1.0,
        )

        score = (
            self._settings.fatigue_weight_velocity * vel_drop
            + self._settings.fatigue_weight_back * back_increase
            + self._settings.fatigue_weight_asymmetry * asym_increase
            + self._settings.fatigue_weight_stability * stability_drop
        )
        return clamp(score, 0.0, 1.0)
