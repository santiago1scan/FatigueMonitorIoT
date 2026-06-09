from __future__ import annotations

import logging

import lgpio

from app.config.settings import Settings
from app.domain.base import BaseGPIO


class RaspberryGPIO(BaseGPIO):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._handle: int | None = None
        self._pin: int | None = None

    async def setup_output(self, pin: int) -> None:
        self._handle = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(self._handle, pin)
        self._pin = pin
        self._logger.info("raspberry_gpio_setup pin=%s", pin)

    async def write(self, pin: int, value: bool) -> None:
        if self._handle is None:
            raise RuntimeError("gpio_not_configured")
        lgpio.gpio_write(self._handle, pin, 1 if value else 0)
        self._logger.info("raspberry_gpio_write pin=%s value=%s", pin, value)
