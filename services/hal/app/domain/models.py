from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class CameraState:
    opened: bool = False


@dataclass
class GpioState:
    configured: bool = False
    last_value: bool | None = None


@dataclass
class HalStatus:
    service: str
    timestamp: datetime
    camera: CameraState
    gpio: GpioState
