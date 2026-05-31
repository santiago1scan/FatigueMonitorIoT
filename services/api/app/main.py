from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging

from app.core.config import Settings
from app.api.routes import router
from app.services.assistant_service import AssistantService
from app.mqtt.mqtt_client import MQTTClient
from app.websocket.connection_manager import ConnectionManager
from app.mqtt.handlers import MQTTHandlers


# Application-level logger
logger = logging.getLogger("assist_api")


def create_app() -> FastAPI:
    """
    Factory to create FastAPI app and wire dependencies.

    Using a factory makes it easier to test and instantiate singletons
    for MQTT client, assistant service and connection manager.
    """
    app = FastAPI(title="Assist API Gateway")

    # CORS for frontend development; restrict in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    settings = Settings()

    # Singletons
    app.state.connection_manager = ConnectionManager()
    app.state.mqtt_client = MQTTClient(host=settings.MQTT_HOST, port=settings.MQTT_PORT)
    app.state.assistant = AssistantService(mqtt_client=app.state.mqtt_client, connection_manager=app.state.connection_manager)

    # Handlers need a reference to the assistant service
    app.state.mqtt_handlers = MQTTHandlers(assistant=app.state.assistant)

    # Background task handle
    app.state._mqtt_task = None


    @app.on_event("startup")
    async def startup_event() -> None:
        logger.info("Starting Assist API Gateway")
        try:
            await app.state.mqtt_client.connect()
        except Exception as exc:
            logger.exception("Failed to connect to MQTT broker: %s", exc)
            raise

        # Start background task to listen for messages
        async def mqtt_listen() -> None:
            try:
                await app.state.mqtt_client.listen(app.state.mqtt_handlers)
            except asyncio.CancelledError:
                return
            except Exception:
                logger.exception("MQTT listening task crashed")

        app.state._mqtt_task = asyncio.create_task(mqtt_listen())


    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        logger.info("Shutting down Assist API Gateway")
        if app.state._mqtt_task:
            app.state._mqtt_task.cancel()
            try:
                await app.state._mqtt_task
            except asyncio.CancelledError:
                pass
        await app.state.mqtt_client.disconnect()


    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        """
        WebSocket endpoint to broadcast FrontendState updates.
        """
        await app.state.connection_manager.connect(websocket)
        try:
            while True:
                # Keep connection alive; clients are passive receivers.
                await websocket.receive_text()
        except WebSocketDisconnect:
            await app.state.connection_manager.disconnect(websocket)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
