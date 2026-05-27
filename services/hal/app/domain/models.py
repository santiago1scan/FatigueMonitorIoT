from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ServoState:
    connected: bool = False
    angle: float | None = None


@dataclass
class CameraState:
    opened: bool = False


@dataclass
class GpioState:
    configured: bool = False
    last_value: bool | None = None


@dataclass
class PwmState:
    active: bool = False
    duty_cycle: float | None = None


@dataclass
class HalStatus:
    service: str
    timestamp: datetime
    servo: ServoState
    camera: CameraState
    gpio: GpioState
    pwm: PwmState
