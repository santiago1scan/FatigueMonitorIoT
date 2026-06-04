from __future__ import annotations

import logging
import threading
import time
from typing import Optional

import cv2
import numpy as np

from app.consumers.base import FrameConsumer, FramePacket


class StreamFrameConsumer(FrameConsumer):
    def __init__(self, stream_url: str, fps_limit: float = 0.0) -> None:
        self._stream_url = stream_url
        self._fps_limit = fps_limit
        self._cap: Optional[cv2.VideoCapture] = None
        self._last_read = 0.0
        self._logger = logging.getLogger("vision.consumer.stream")
        self._last_warn = 0.0

        self._latest_frame: Optional[np.ndarray] = None
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def open(self) -> None:
        self._cap = cv2.VideoCapture(self._stream_url)
        if not self._cap.isOpened():
            self._logger.warning("stream_open_failed url=%s", self._stream_url)
            return

        self._running = True
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()

    def _reader_loop(self) -> None:
        while self._running:
            if self._cap is None or not self._cap.isOpened():
                time.sleep(0.01)
                continue
            ok, frame = self._cap.read()
            if ok:
                with self._lock:
                    self._latest_frame = frame
            else:
                time.sleep(0.005)

    def read(self) -> Optional[FramePacket]:
        if self._cap is None or not self._cap.isOpened():
            self._warn_throttled("stream_not_opened")
            return None

        if self._fps_limit > 0:
            now = time.monotonic()
            min_interval = 1.0 / self._fps_limit
            if now - self._last_read < min_interval:
                return None

        with self._lock:
            frame = self._latest_frame
            self._latest_frame = None

        if frame is None:
            return None

        self._last_read = time.monotonic()
        return FramePacket(frame_bgr=frame, timestamp=time.time())

    def close(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        if self._cap is not None:
            self._cap.release()

    def _warn_throttled(self, message: str) -> None:
        now = time.monotonic()
        if now - self._last_warn >= 5.0:
            self._logger.warning("%s url=%s", message, self._stream_url)
            self._last_warn = now
