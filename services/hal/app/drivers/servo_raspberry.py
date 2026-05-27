from __future__ import annotations

import logging

from app.config.settings import Settings
from app.domain.base import BaseServo


class RaspberryServo(BaseServo):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._servo = None

    async def connect(self) -> None:
        try:
            from gpiozero import Servo as GpioServo
        except ImportError as exc:
            raise RuntimeError("gpiozero is required for RaspberryServo") from exc

        self._servo = GpioServo(self._settings.servo_pin)
        self._logger.info("raspberry_servo_connected pin=%s", self._settings.servo_pin)

    async def disconnect(self) -> None:
        if self._servo:
            self._servo.detach()
            self._servo = None
            self._logger.info("raspberry_servo_disconnected")

    async def move(self, angle: float) -> None:
        if not self._servo:
            raise RuntimeError("servo_not_connected")
        normalized = (angle - self._settings.servo_min_angle) / (
            self._settings.servo_max_angle - self._settings.servo_min_angle
        )
        normalized = max(0.0, min(normalized, 1.0))
        value = (normalized * 2.0) - 1.0
        self._servo.value = value
        self._logger.info("raspberry_servo_move angle=%s value=%s", angle, value)
