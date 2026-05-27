from __future__ import annotations

import logging

from app.config.settings import Settings
from app.domain.base import BaseGPIO


class RaspberryGPIO(BaseGPIO):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._device = None

    async def setup_output(self, pin: int) -> None:
        try:
            from gpiozero import DigitalOutputDevice
        except ImportError as exc:
            raise RuntimeError("gpiozero is required for RaspberryGPIO") from exc

        self._device = DigitalOutputDevice(pin)
        self._logger.info("raspberry_gpio_setup pin=%s", pin)

    async def write(self, pin: int, value: bool) -> None:
        if not self._device:
            raise RuntimeError("gpio_not_configured")
        if value:
            self._device.on()
        else:
            self._device.off()
        self._logger.info("raspberry_gpio_write pin=%s value=%s", pin, value)
