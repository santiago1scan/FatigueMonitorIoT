from __future__ import annotations

import asyncio
import logging

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
        return b""
