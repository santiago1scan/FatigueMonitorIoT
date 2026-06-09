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
        result = subprocess.run(
            ["gpioset", "gpiochip0", f"{self._pin}={state}"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self._logger.error(
                "gpioset_failed rc=%s stderr=%s", result.returncode, result.stderr.strip()
            )
            raise RuntimeError(f"gpioset failed: {result.stderr.strip()}")
        self._logger.info("raspberry_gpio_write pin=%s value=%s", pin, value)
