from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol


class BaseServo(ABC):
    @abstractmethod
    async def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def move(self, angle: float) -> None:
        raise NotImplementedError


class BaseCamera(ABC):
    @abstractmethod
    async def open(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_frame(self) -> bytes:
        raise NotImplementedError


class BaseGPIO(ABC):
    @abstractmethod
    async def setup_output(self, pin: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def write(self, pin: int, value: bool) -> None:
        raise NotImplementedError


class BasePWM(ABC):
    @abstractmethod
    async def start(self, pin: int, frequency: int, duty_cycle: float) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set_duty_cycle(self, duty_cycle: float) -> None:
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        raise NotImplementedError


class HealthReporter(Protocol):
    async def publish_health(self) -> None: ...
