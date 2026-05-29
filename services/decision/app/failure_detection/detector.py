from __future__ import annotations

import time
from dataclasses import dataclass

from app.biomechanics.features import BiomechFeatures
from app.config.settings import Settings
from app.state_machine.machine import StateUpdate
from app.state_machine.states import BiomechState


@dataclass
class FailureEvent:
    event: str
    confidence: float


class FailureDetector:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._sticking_start: float | None = None
        self._near_failure_sent = False

    def update(self, features: BiomechFeatures, state_update: StateUpdate) -> FailureEvent | None:
        if state_update.state != BiomechState.ASCENDING:
            self._reset()
            return None

        velocity = abs(features.velocity_vertical)
        if velocity > self._settings.near_failure_velocity_abs:
            self._reset()
            return None

        now = time.monotonic()
        if self._sticking_start is None:
            self._sticking_start = now

        elapsed = now - self._sticking_start
        if elapsed >= self._settings.failure_sticking_s:
            return FailureEvent(event="FAILURE_DETECTED", confidence=state_update.confidence)

        if elapsed >= self._settings.near_failure_sticking_s and not self._near_failure_sent:
            self._near_failure_sent = True
            return FailureEvent(event="NEAR_FAILURE", confidence=state_update.confidence)

        return None

    def _reset(self) -> None:
        self._sticking_start = None
        self._near_failure_sent = False
