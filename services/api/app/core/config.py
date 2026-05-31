from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration using environment variables.

    Using `BaseSettings` (pydantic v2) centralizes configuration
    and enables easy overrides via environment in production.
    """

    MQTT_HOST: str = "mqtt"
    MQTT_PORT: int = 1883
    LOG_LEVEL: str = "INFO"

    class Config:
        env_prefix = "ASSIST_"
