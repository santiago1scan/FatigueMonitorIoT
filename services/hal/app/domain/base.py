from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol


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


class HealthReporter(Protocol):
    async def publish_health(self) -> None: ...
