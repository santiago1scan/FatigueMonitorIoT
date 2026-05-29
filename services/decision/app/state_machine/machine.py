from __future__ import annotations

from dataclasses import dataclass

from app.biomechanics.features import BiomechFeatures
from app.biomechanics.types import SmoothedFrame
from app.config.settings import Settings
from app.state_machine.states import BiomechState
from app.utils.math import clamp


@dataclass
class StateUpdate:
    state: BiomechState
    previous_state: BiomechState
    changed: bool
    confidence: float


class BiomechStateMachine:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._state = BiomechState.IDLE
        self._candidate = BiomechState.IDLE
        self._candidate_count = 0
        self._transition_count = 0

    @property
    def state(self) -> BiomechState:
        return self._state

    @property
    def transition_count(self) -> int:
        return self._transition_count

    def force_state(self, state: BiomechState, confidence: float) -> StateUpdate:
        previous = self._state
        self._state = state
        self._candidate = state
        self._candidate_count = self._settings.min_confirm_frames
        self._transition_count += 1
        return StateUpdate(
            state=self._state,
            previous_state=previous,
            changed=previous != self._state,
            confidence=confidence,
        )

    def update(self, features: BiomechFeatures, frame: SmoothedFrame) -> StateUpdate:
        candidate = self._resolve_candidate(features, frame)
        if candidate != self._candidate:
            self._candidate = candidate
            self._candidate_count = 1
        else:
            self._candidate_count += 1

        previous = self._state
        if candidate != self._state and self._candidate_count >= self._settings.min_confirm_frames:
            self._state = candidate
            self._transition_count += 1

        confidence = clamp(frame.confidence * features.stability, 0.0, 1.0)
        return StateUpdate(
            state=self._state,
            previous_state=previous,
            changed=previous != self._state,
            confidence=confidence,
        )

    def _resolve_candidate(self, features: BiomechFeatures, frame: SmoothedFrame) -> BiomechState:
        if not frame.tracking or frame.confidence < self._settings.min_confidence_lost:
            return BiomechState.TRACKING_LOST
        if frame.confidence < self._settings.min_confidence_unstable:
            return BiomechState.TRACKING_UNSTABLE

        knee_avg = features.knee_angle_avg
        velocity = features.velocity_vertical

        if knee_avg is None:
            return BiomechState.IDLE

        if self._state in (BiomechState.STANDING, BiomechState.LOCKOUT):
            if (
                knee_avg >= self._settings.standing_knee_angle_min - self._settings.knee_hysteresis_deg
                and abs(velocity) <= self._settings.vel_idle_threshold
            ):
                return self._state

        if self._state == BiomechState.BOTTOM:
            if (
                knee_avg <= self._settings.bottom_knee_angle_max + self._settings.knee_hysteresis_deg
                and abs(velocity) <= self._settings.vel_idle_threshold
            ):
                return BiomechState.BOTTOM

        if (
            knee_avg >= self._settings.standing_knee_angle_min
            and abs(velocity) <= self._settings.vel_idle_threshold
        ):
            if self._state == BiomechState.ASCENDING:
                return BiomechState.LOCKOUT
            return BiomechState.STANDING

        if (
            knee_avg <= self._settings.bottom_knee_angle_max
            and abs(velocity) <= self._settings.vel_idle_threshold
        ):
            return BiomechState.BOTTOM

        if velocity <= self._settings.vel_descend_threshold:
            return BiomechState.DESCENDING

        if velocity >= self._settings.vel_ascend_threshold:
            return BiomechState.ASCENDING

        return self._state
