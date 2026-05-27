from __future__ import annotations

import asyncio
import logging

from app.config.settings import Settings
from app.domain.base import BaseGPIO


class MockGPIO(BaseGPIO):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)

    async def setup_output(self, pin: int) -> None:
        await asyncio.sleep(0)
        self._logger.info("mock_gpio_setup pin=%s", pin)

    async def write(self, pin: int, value: bool) -> None:
        await asyncio.sleep(0)
        self._logger.info("mock_gpio_write pin=%s value=%s", pin, value)
