from __future__ import annotations

import logging

from app.config.settings import Settings
from app.domain.base import BasePWM


class RaspberryPWM(BasePWM):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._device = None

    async def start(self, pin: int, frequency: int, duty_cycle: float) -> None:
        try:
            from gpiozero import PWMOutputDevice
        except ImportError as exc:
            raise RuntimeError("gpiozero is required for RaspberryPWM") from exc

        self._device = PWMOutputDevice(pin, frequency=frequency)
        await self.set_duty_cycle(duty_cycle)
        self._logger.info("raspberry_pwm_start pin=%s frequency=%s", pin, frequency)

    async def set_duty_cycle(self, duty_cycle: float) -> None:
        if not self._device:
            raise RuntimeError("pwm_not_started")
        value = max(0.0, min(duty_cycle, 100.0)) / 100.0
        self._device.value = value
        self._logger.info("raspberry_pwm_duty_cycle value=%s", value)

    async def stop(self) -> None:
        if self._device:
            self._device.close()
            self._device = None
            self._logger.info("raspberry_pwm_stop")
