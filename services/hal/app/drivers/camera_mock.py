from __future__ import annotations

import asyncio
import logging
import time

import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

from app.config.settings import Settings
from app.domain.base import BaseCamera


class MockCamera(BaseCamera):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._opened = False

    async def open(self) -> None:
        await asyncio.sleep(0)
        self._opened = True
        self._logger.info("mock_camera_opened")

    async def close(self) -> None:
        await asyncio.sleep(0)
        self._opened = False
        self._logger.info("mock_camera_closed")

    async def get_frame(self) -> bytes:
        await asyncio.sleep(0)
        if not self._opened:
            raise RuntimeError("camera_not_opened")
        if cv2 is None:
            return b""
        width = self._settings.camera_frame_width
        height = self._settings.camera_frame_height
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        label = time.strftime("%H:%M:%S")
        cv2.putText(
            frame,
            f"Mock Frame {label}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2,
        )
        ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ok:
            return b""
        return encoded.tobytes()
