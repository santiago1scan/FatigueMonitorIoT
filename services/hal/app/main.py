from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import build_router
from app.config.settings import Settings
from app.mqtt.client import MqttClient
from app.mqtt.handlers import MqttHandlers
from app.services.app_context import AppContext
from app.utils.logging import configure_logging


def create_app() -> FastAPI:
    settings = Settings()
    configure_logging(settings.log_level)
    context = AppContext.build(settings)
    handlers = MqttHandlers(context)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await context.start()
        mqtt_client = MqttClient(settings, handlers.handle)
        context.mqtt_client = mqtt_client
        await mqtt_client.start(handlers.publish_health)
        yield
        await mqtt_client.stop()
        await context.stop()

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(build_router(context))
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:create_app",
        host="0.0.0.0",
        port=Settings().api_port,
        factory=True,
        log_level=Settings().log_level.lower(),
    )
