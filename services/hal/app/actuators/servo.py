from __future__ import annotations

import logging

from app.config.settings import Settings
from app.domain.base import BaseServo


class ServoService:
    def __init__(self, driver: BaseServo, settings: Settings) -> None:
        self._driver = driver
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self.connected = False
        self.last_angle: float | None = None

    async def connect(self) -> None:
        await self._driver.connect()
        self.connected = True
        await self.move(self._settings.servo_neutral_angle)

    async def disconnect(self) -> None:
        await self._driver.disconnect()
        self.connected = False

    async def move(self, angle: float) -> None:
        bounded = max(self._settings.servo_min_angle, min(angle, self._settings.servo_max_angle))
        await self._driver.move(bounded)
        self.last_angle = bounded
        self._logger.info("servo_move angle=%s", bounded)

    async def activate(self, force: float) -> None:
        force = max(0.0, min(force, 1.0))
        angle = self._settings.servo_min_angle + (
            (self._settings.servo_max_angle - self._settings.servo_min_angle) * force
        )
        await self.move(angle)

    async def disable(self) -> None:
        await self.move(self._settings.servo_neutral_angle)

    async def test_move(self, angle: float | None, force: float | None) -> None:
        if angle is not None:
            await self.move(angle)
            return
        if force is not None:
            await self.activate(force)
            return
        await self.move(self._settings.servo_neutral_angle)
