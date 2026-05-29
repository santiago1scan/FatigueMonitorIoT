from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InternalSnapshot:
    frames_received: int
    frames_processed: int
    frames_invalid: int
    frames_dropped: int
    state_transitions: int
    last_processing_ms: float
    queue_size: int


class InternalMetrics:
    def __init__(self) -> None:
        self._frames_received = 0
        self._frames_processed = 0
        self._frames_invalid = 0
        self._frames_dropped = 0
        self._state_transitions = 0
        self._last_processing_ms = 0.0
        self._queue_size = 0

    def record_received(self) -> None:
        self._frames_received += 1

    def record_processed(self, processing_ms: float, queue_size: int) -> None:
        self._frames_processed += 1
        self._last_processing_ms = processing_ms
        self._queue_size = queue_size

    def record_invalid(self) -> None:
        self._frames_invalid += 1

    def record_dropped(self) -> None:
        self._frames_dropped += 1

    def record_transition(self) -> None:
        self._state_transitions += 1

    def snapshot(self) -> InternalSnapshot:
        return InternalSnapshot(
            frames_received=self._frames_received,
            frames_processed=self._frames_processed,
            frames_invalid=self._frames_invalid,
            frames_dropped=self._frames_dropped,
            state_transitions=self._state_transitions,
            last_processing_ms=self._last_processing_ms,
            queue_size=self._queue_size,
        )
