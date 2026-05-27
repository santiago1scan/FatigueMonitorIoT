from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from datetime import datetime

from app.actuators.servo import ServoService
from app.camera.camera_service import CameraService
from app.config.settings import Settings
from app.domain.models import CameraState, GpioState, HalStatus, PwmState, ServoState
from app.drivers.camera_mock import MockCamera
from app.drivers.camera_opencv import OpenCVCamera
from app.drivers.gpio_mock import MockGPIO
from app.drivers.gpio_raspberry import RaspberryGPIO
from app.drivers.pwm_mock import MockPWM
from app.drivers.pwm_raspberry import RaspberryPWM
from app.drivers.servo_mock import MockServo
from app.drivers.servo_raspberry import RaspberryServo
from app.gpio.gpio_service import GPIOService
from app.gpio.pwm_service import PWMService

if TYPE_CHECKING:
    from app.mqtt.client import MqttClient


@dataclass
class AppContext:
    settings: Settings
    servo_service: ServoService
    camera_service: CameraService
    gpio_service: GPIOService
    pwm_service: PWMService
    mqtt_client: "MqttClient" | None = None

    @classmethod
    def build(cls, settings: Settings) -> "AppContext":
        servo_driver = cls._build_servo(settings)
        camera_driver = cls._build_camera(settings)
        gpio_driver = cls._build_gpio(settings)
        pwm_driver = cls._build_pwm(settings)

        return cls(
            settings=settings,
            servo_service=ServoService(servo_driver, settings),
            camera_service=CameraService(camera_driver, settings),
            gpio_service=GPIOService(gpio_driver, settings),
            pwm_service=PWMService(pwm_driver, settings),
        )

    @staticmethod
    def _build_servo(settings: Settings):
        provider = settings.servo_provider.lower()
        if provider == "raspberry":
            return RaspberryServo(settings)
        return MockServo(settings)

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

    @staticmethod
    def _build_pwm(settings: Settings):
        provider = settings.pwm_provider.lower()
        if provider == "raspberry":
            return RaspberryPWM(settings)
        return MockPWM(settings)

    async def start(self) -> None:
        await self.servo_service.connect()
        await self.camera_service.open()
        await self.gpio_service.configure()
        await self.pwm_service.start()

    async def stop(self) -> None:
        await self.pwm_service.stop()
        await self.gpio_service.shutdown()
        await self.camera_service.close()
        await self.servo_service.disconnect()

    def build_status(self) -> HalStatus:
        return HalStatus(
            service=self.settings.app_name,
            timestamp=datetime.utcnow(),
            servo=ServoState(
                connected=self.servo_service.connected,
                angle=self.servo_service.last_angle,
            ),
            camera=CameraState(opened=self.camera_service.opened),
            gpio=GpioState(
                configured=self.gpio_service.configured,
                last_value=self.gpio_service.last_value,
            ),
            pwm=PwmState(
                active=self.pwm_service.active,
                duty_cycle=self.pwm_service.duty_cycle,
            ),
        )
