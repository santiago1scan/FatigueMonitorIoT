from __future__ import annotations

import asyncio
import logging

from app.config.settings import Settings
from app.domain.base import BasePWM


class MockPWM(BasePWM):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)

    async def start(self, pin: int, frequency: int, duty_cycle: float) -> None:
        await asyncio.sleep(0)
        self._logger.info(
            "mock_pwm_start pin=%s frequency=%s duty_cycle=%s", pin, frequency, duty_cycle
        )

    async def set_duty_cycle(self, duty_cycle: float) -> None:
        await asyncio.sleep(0)
        self._logger.info("mock_pwm_duty_cycle value=%s", duty_cycle)

    async def stop(self) -> None:
        await asyncio.sleep(0)
        self._logger.info("mock_pwm_stop")
