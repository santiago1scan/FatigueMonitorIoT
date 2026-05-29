from __future__ import annotations

import time
from dataclasses import dataclass

from app.biomechanics.features import BiomechFeatures
from app.config.settings import Settings
from app.state_machine.machine import StateUpdate
from app.state_machine.states import BiomechState


@dataclass
class RepEvent:
    rep_count: int
    depth_ok: bool


class RepCounter:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._rep_count = 0
        self._stage = 0
        self._saw_bottom = False
        self._last_rep_time = 0.0
        self._depth_ok = False

    @property
    def rep_count(self) -> int:
        return self._rep_count

    def update(self, state_update: StateUpdate, features: BiomechFeatures) -> RepEvent | None:
        if not state_update.changed:
            return None

        state = state_update.state
        if state in (BiomechState.TRACKING_LOST, BiomechState.TRACKING_UNSTABLE, BiomechState.IDLE):
            self._reset()
            return None

        if state == BiomechState.DESCENDING and self._stage == 0:
            self._stage = 1
            return None

        if state == BiomechState.BOTTOM and self._stage == 1:
            self._stage = 2
            self._saw_bottom = True
            self._depth_ok = features.depth_score >= self._settings.depth_score_min
            return None

        if state == BiomechState.ASCENDING and self._stage == 2:
            self._stage = 3
            return None

        if state == BiomechState.LOCKOUT and self._stage == 3:
            now = time.monotonic()
            if now - self._last_rep_time >= self._settings.min_rep_interval_s:
                self._rep_count += 1
                self._last_rep_time = now
                event = RepEvent(rep_count=self._rep_count, depth_ok=self._depth_ok and self._saw_bottom)
                self._reset()
                return event
            self._reset()
            return None

        if state == BiomechState.STANDING and self._stage > 0:
            self._reset()

        return None

    def _reset(self) -> None:
        self._stage = 0
        self._saw_bottom = False
        self._depth_ok = False
