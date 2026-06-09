from __future__ import annotations

from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "hal-service"
    env: str = "dev"
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8080

    mqtt_host: str = "mqtt"
    mqtt_port: int = 1883
    mqtt_username: str | None = None
    mqtt_password: str | None = None
    mqtt_client_id: str = "hal-service"
    mqtt_topics: List[str] = Field(
        default_factory=lambda: [
            "gym/assist/disable",
            "gym/decision/failure",
        ]
    )
    mqtt_status_topic: str = "gym/system/status"
    mqtt_health_topic: str = "gym/hal/health"
    mqtt_error_topic: str = "gym/hal/errors"
    mqtt_status_interval_s: int = 5

    camera_provider: str = "mock"
    camera_device_index: int = 0
    camera_frame_width: int = 640
    camera_frame_height: int = 480

    gpio_provider: str = "mock"
    status_led_pin: int = 17

    @field_validator("mqtt_topics", mode="before")
    @classmethod
    def _split_topics(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    class Config:
        env_prefix = "HAL_"
        case_sensitive = False
