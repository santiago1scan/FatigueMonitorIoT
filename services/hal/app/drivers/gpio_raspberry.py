from __future__ import annotations

import logging

import gpiod
from gpiod.line import Direction, Value

from app.config.settings import Settings
from app.domain.base import BaseGPIO


class RaspberryGPIO(BaseGPIO):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._request: gpiod.LineRequest | None = None
        self._pin: int | None = None

    async def setup_output(self, pin: int) -> None:
        self._request = gpiod.request_lines(
            "/dev/gpiochip0",
            consumer="hal",
            config={
                pin: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE),
            },
        )
        self._pin = pin
        self._logger.info("raspberry_gpio_setup pin=%s", pin)

    async def write(self, pin: int, value: bool) -> None:
        if self._request is None:
            raise RuntimeError("gpio_not_configured")
        self._request.set_value(pin, Value.ACTIVE if value else Value.INACTIVE)
        self._logger.info("raspberry_gpio_write pin=%s value=%s", pin, value)
