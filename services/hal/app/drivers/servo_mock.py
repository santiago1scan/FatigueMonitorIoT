from __future__ import annotations

import asyncio
import logging

from app.config.settings import Settings
from app.domain.base import BaseServo


class MockServo(BaseServo):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)

    async def connect(self) -> None:
        await asyncio.sleep(0)
        self._logger.info("mock_servo_connected")

    async def disconnect(self) -> None:
        await asyncio.sleep(0)
        self._logger.info("mock_servo_disconnected")

    async def move(self, angle: float) -> None:
        await asyncio.sleep(0)
        self._logger.info("mock_servo_move angle=%s", angle)
