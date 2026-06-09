from __future__ import annotations

import logging

from periphery import GPIO

from app.config.settings import Settings
from app.domain.base import BaseGPIO


class RaspberryGPIO(BaseGPIO):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._gpio: GPIO | None = None

    async def setup_output(self, pin: int) -> None:
        self._gpio = GPIO(pin, "out")
        self._logger.info("raspberry_gpio_setup pin=%s", pin)

    async def write(self, pin: int, value: bool) -> None:
        if self._gpio is None:
            raise RuntimeError("gpio_not_configured")
        self._gpio.write(value)
        self._logger.info("raspberry_gpio_write pin=%s value=%s", pin, value)
