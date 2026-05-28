from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import time
from typing import Deque, Optional


@dataclass
class InternalMetricsSnapshot:
    fps: float
    inference_ms_avg: float
    frames_processed: int
    frames_dropped: int
    tracking: bool
    last_pipeline_latency_ms: float


class InternalMetrics:
    def __init__(self) -> None:
        self._frames_processed = 0
        self._frames_dropped = 0
        self._last_frame_time: Optional[float] = None
        self._last_fps_time = time.monotonic()
        self._frame_counter = 0
        self._fps = 0.0
        self._inference_times: Deque[float] = deque(maxlen=50)
        self._tracking = False
        self._last_pipeline_latency_ms = 0.0

    def record_frame(self) -> None:
        self._frames_processed += 1
        self._frame_counter += 1
        now = time.monotonic()
        if now - self._last_fps_time >= 1.0:
            self._fps = self._frame_counter / (now - self._last_fps_time)
            self._frame_counter = 0
            self._last_fps_time = now
        self._last_frame_time = now

    def record_dropped(self) -> None:
        self._frames_dropped += 1

    def record_inference(self, inference_sec: float) -> None:
        self._inference_times.append(inference_sec)

    def set_tracking(self, tracking: bool) -> None:
        self._tracking = tracking

    def set_pipeline_latency_ms(self, latency_ms: float) -> None:
        self._last_pipeline_latency_ms = latency_ms

    def snapshot(self) -> InternalMetricsSnapshot:
        if self._inference_times:
            avg = sum(self._inference_times) / len(self._inference_times)
        else:
            avg = 0.0
        return InternalMetricsSnapshot(
            fps=self._fps,
            inference_ms_avg=avg * 1000.0,
            frames_processed=self._frames_processed,
            frames_dropped=self._frames_dropped,
            tracking=self._tracking,
            last_pipeline_latency_ms=self._last_pipeline_latency_ms,
        )
