from __future__ import annotations

import logging
import time
from typing import Optional

import cv2

from app.consumers.base import FrameConsumer, FramePacket


class StreamFrameConsumer(FrameConsumer):
    def __init__(self, stream_url: str, fps_limit: float = 0.0) -> None:
        self._stream_url = stream_url
        self._fps_limit = fps_limit
        self._cap: Optional[cv2.VideoCapture] = None
        self._last_read = 0.0
        self._logger = logging.getLogger("vision.consumer.stream")
        self._last_warn = 0.0

    def open(self) -> None:
        self._cap = cv2.VideoCapture(self._stream_url)
        if not self._cap.isOpened():
            self._logger.warning("stream_open_failed url=%s", self._stream_url)

    def read(self) -> Optional[FramePacket]:
        if self._cap is None or not self._cap.isOpened():
            self._warn_throttled("stream_not_opened")
            return None

        if self._fps_limit > 0:
            now = time.monotonic()
            min_interval = 1.0 / self._fps_limit
            if now - self._last_read < min_interval:
                return None

        ok, frame = self._cap.read()
        if not ok:
            self._warn_throttled("stream_read_failed")
            return None

        self._last_read = time.monotonic()
        return FramePacket(frame_bgr=frame, timestamp=time.time())

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()

    def _warn_throttled(self, message: str) -> None:
        now = time.monotonic()
        if now - self._last_warn >= 5.0:
            self._logger.warning("%s url=%s", message, self._stream_url)
            self._last_warn = now
