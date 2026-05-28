from __future__ import annotations

import logging

from app.config.settings import Settings
from app.domain.base import BaseCamera


class OpenCVCamera(BaseCamera):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._capture = None

    async def open(self) -> None:
        try:
            import cv2
        except ImportError as exc:
            raise RuntimeError("opencv-python-headless is required for OpenCVCamera") from exc

        self._capture = cv2.VideoCapture(self._settings.camera_device_index)
        self._capture.set(3, self._settings.camera_frame_width)
        self._capture.set(4, self._settings.camera_frame_height)
        self._logger.info("opencv_camera_opened device=%s", self._settings.camera_device_index)

    async def close(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None
            self._logger.info("opencv_camera_closed")

    async def get_frame(self) -> bytes:
        if self._capture is None:
            raise RuntimeError("camera_not_opened")
        ok, frame = self._capture.read()
        if not ok:
            raise RuntimeError("camera_capture_failed")
        try:
            import cv2
        except ImportError as exc:
            raise RuntimeError("opencv-python-headless is required for OpenCVCamera") from exc
        ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ok:
            raise RuntimeError("camera_encode_failed")
        return encoded.tobytes()
