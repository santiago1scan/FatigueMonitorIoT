from __future__ import annotations

import logging

from app.config.settings import Settings
from app.domain.base import BasePWM


class PWMService:
    def __init__(self, driver: BasePWM, settings: Settings) -> None:
        self._driver = driver
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self.active = False
        self.duty_cycle: float | None = None

    async def start(self) -> None:
        await self._driver.start(
            self._settings.pwm_pin,
            self._settings.pwm_frequency,
            0.0,
        )
        self.active = True
        self.duty_cycle = 0.0

    async def set_duty_cycle(self, duty_cycle: float) -> None:
        duty_cycle = max(0.0, min(duty_cycle, 100.0))
        await self._driver.set_duty_cycle(duty_cycle)
        self.duty_cycle = duty_cycle
        self._logger.info("pwm_duty_cycle value=%s", duty_cycle)

    async def stop(self) -> None:
        if self.active:
            await self._driver.stop()
            self.active = False
            self.duty_cycle = None
