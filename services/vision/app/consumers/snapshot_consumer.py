from __future__ import annotations

import logging
import time
from typing import Optional

import cv2
import numpy as np
import requests

from app.consumers.base import FrameConsumer, FramePacket


class SnapshotFrameConsumer(FrameConsumer):
    def __init__(self, snapshot_url: str, fps_limit: float = 0.0) -> None:
        self._snapshot_url = snapshot_url
        self._fps_limit = fps_limit
        self._last_read = 0.0
        self._session = requests.Session()
        self._logger = logging.getLogger("vision.consumer.snapshot")
        self._last_warn = 0.0

    def open(self) -> None:
        return None

    def read(self) -> Optional[FramePacket]:
        if self._fps_limit > 0:
            now = time.monotonic()
            min_interval = 1.0 / self._fps_limit
            if now - self._last_read < min_interval:
                return None

        try:
            response = self._session.get(self._snapshot_url, timeout=1.5)
        except requests.RequestException:
            self._warn_throttled("snapshot_request_failed")
            return None

        if response.status_code != 200:
            self._warn_throttled(
                f"snapshot_bad_status status={response.status_code}"
            )
            return None

        data = np.frombuffer(response.content, dtype=np.uint8)
        frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if frame is None:
            self._warn_throttled("snapshot_decode_failed")
            return None

        self._last_read = time.monotonic()
        return FramePacket(frame_bgr=frame, timestamp=time.time())

    def close(self) -> None:
        self._session.close()

    def _warn_throttled(self, message: str) -> None:
        now = time.monotonic()
        if now - self._last_warn >= 5.0:
            self._logger.warning("%s url=%s", message, self._snapshot_url)
            self._last_warn = now
