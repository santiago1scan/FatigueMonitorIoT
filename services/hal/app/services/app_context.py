from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from datetime import datetime

from app.camera.camera_service import CameraService
from app.config.settings import Settings
from app.domain.models import CameraState, GpioState, HalStatus
from app.drivers.camera_mock import MockCamera
from app.drivers.camera_opencv import OpenCVCamera
from app.drivers.gpio_mock import MockGPIO
from app.drivers.gpio_raspberry import RaspberryGPIO
from app.gpio.gpio_service import GPIOService

if TYPE_CHECKING:
    from app.mqtt.client import MqttClient


@dataclass
class AppContext:
    settings: Settings
    camera_service: CameraService
    gpio_service: GPIOService
    mqtt_client: "MqttClient" | None = None

    @classmethod
    def build(cls, settings: Settings) -> "AppContext":
        camera_driver = cls._build_camera(settings)
        gpio_driver = cls._build_gpio(settings)

        return cls(
            settings=settings,
            camera_service=CameraService(camera_driver, settings),
            gpio_service=GPIOService(gpio_driver, settings),
        )

    @staticmethod
    def _build_camera(settings: Settings):
        provider = settings.camera_provider.lower()
        if provider == "opencv":
            return OpenCVCamera(settings)
        return MockCamera(settings)

    @staticmethod
    def _build_gpio(settings: Settings):
        provider = settings.gpio_provider.lower()
        if provider == "raspberry":
            return RaspberryGPIO(settings)
        return MockGPIO(settings)

    async def start(self) -> None:
        await self.camera_service.open()
        await self.gpio_service.configure()

    async def stop(self) -> None:
        await self.gpio_service.shutdown()
        await self.camera_service.close()

    def build_status(self) -> HalStatus:
        return HalStatus(
            service=self.settings.app_name,
            timestamp=datetime.utcnow(),
            camera=CameraState(opened=self.camera_service.opened),
            gpio=GpioState(
                configured=self.gpio_service.configured,
                last_value=self.gpio_service.last_value,
            ),
        )
