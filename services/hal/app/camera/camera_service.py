from __future__ import annotations

import logging

from app.config.settings import Settings
from app.domain.base import BaseCamera


class CameraService:
    def __init__(self, driver: BaseCamera, settings: Settings) -> None:
        self._driver = driver
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self.opened = False

    async def open(self) -> None:
        await self._driver.open()
        self.opened = True
        self._logger.info("camera_opened device=%s", self._settings.camera_device_index)

    async def close(self) -> None:
        await self._driver.close()
        self.opened = False
        self._logger.info("camera_closed")

    async def get_frame(self) -> bytes:
        return await self._driver.get_frame()
