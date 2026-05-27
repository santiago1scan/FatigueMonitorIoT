from __future__ import annotations

import logging

from app.config.settings import Settings
from app.domain.base import BaseGPIO


class GPIOService:
    def __init__(self, driver: BaseGPIO, settings: Settings) -> None:
        self._driver = driver
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self.configured = False
        self.last_value: bool | None = None

    async def configure(self) -> None:
        await self._driver.setup_output(self._settings.status_led_pin)
        self.configured = True

    async def set_status_led(self, enabled: bool) -> None:
        await self._driver.write(self._settings.status_led_pin, enabled)
        self.last_value = enabled
        self._logger.info("gpio_write pin=%s value=%s", self._settings.status_led_pin, enabled)

    async def shutdown(self) -> None:
        if self.configured:
            await self.set_status_led(False)
            self.configured = False
