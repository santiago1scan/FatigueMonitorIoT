from __future__ import annotations

import asyncio
import logging

import cv2

from app.config.settings import Settings
from app.domain.base import BaseCamera


class OpenCVCamera(BaseCamera):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._capture = None
        self._loop: asyncio.AbstractEventLoop | None = None

    async def open(self) -> None:
        self._loop = asyncio.get_event_loop()
        self._capture = cv2.VideoCapture(self._settings.camera_device_index)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self._settings.camera_frame_width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self._settings.camera_frame_height)
        self._capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self._logger.info("opencv_camera_opened device=%s", self._settings.camera_device_index)

    async def close(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None
            self._logger.info("opencv_camera_closed")

    async def get_frame(self) -> bytes:
        if self._capture is None:
            raise RuntimeError("camera_not_opened")
        loop = self._loop or asyncio.get_event_loop()
        ok, frame = await loop.run_in_executor(None, self._capture.read)
        if not ok:
            raise RuntimeError("camera_capture_failed")
        ok, encoded = await loop.run_in_executor(
            None,
            lambda: cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80]),
        )
        if not ok:
            raise RuntimeError("camera_encode_failed")
        return encoded.tobytes()
