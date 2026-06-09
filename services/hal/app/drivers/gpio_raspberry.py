from __future__ import annotations

import asyncio
import logging
import os

from app.config.settings import Settings
from app.domain.base import BaseGPIO


class RaspberryGPIO(BaseGPIO):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._pin: int | None = None

    async def setup_output(self, pin: int) -> None:
        self._pin = pin
        gpio_path = f"/sys/class/gpio/gpio{pin}"
        if not os.path.exists(gpio_path):
            with open("/sys/class/gpio/export", "w") as f:
                f.write(str(pin))
            await asyncio.sleep(0.1)
        with open(f"{gpio_path}/direction", "w") as f:
            f.write("out")
        self._logger.info("raspberry_gpio_setup pin=%s", pin)

    async def write(self, pin: int, value: bool) -> None:
        if self._pin is None:
            raise RuntimeError("gpio_not_configured")
        with open(f"/sys/class/gpio/gpio{pin}/value", "w") as f:
            f.write("1" if value else "0")
        self._logger.info("raspberry_gpio_write pin=%s value=%s", pin, value)
