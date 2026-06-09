from __future__ import annotations

import logging
import subprocess

from app.config.settings import Settings
from app.domain.base import BaseGPIO


class RaspberryGPIO(BaseGPIO):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._pin: int | None = None

    async def setup_output(self, pin: int) -> None:
        self._pin = pin
        self._logger.info("raspberry_gpio_setup pin=%s", pin)

    async def write(self, pin: int, value: bool) -> None:
        if self._pin is None:
            raise RuntimeError("gpio_not_configured")
        state = "1" if value else "0"
        subprocess.run(
            ["gpioset", "gpiochip0", f"{self._pin}={state}"],
            check=True,
            capture_output=True,
            text=True,
        )
        self._logger.info("raspberry_gpio_write pin=%s value=%s", pin, value)
