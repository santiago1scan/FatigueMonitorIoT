import asyncio
import json
import logging
from typing import Optional

from aiomqtt import Client, MqttError

logger = logging.getLogger("assist_api.mqtt")


class MQTTClient:
    """
    Lightweight async MQTT client wrapper using `aiomqtt`.

    Responsibilities:
    - Manage connection lifecycle
    - Provide publish helpers for assist commands
    - Expose a `listen(handlers)` coroutine that subscribes to required
      topics and dispatches messages to handler methods.

    This class keeps a minimal public surface so business logic can use
    high-level methods like `publish_activate()`.
    """

    def __init__(self, host: str = "mqtt", port: int = 1883) -> None:
        self.host = host
        self.port = port
        self._client: Optional[Client] = None
        self._connected = False

    async def connect(self) -> None:
        self._client = Client(hostname=self.host, port=self.port)
        try:
            await self._client.__aenter__()
            self._connected = True
            logger.info("Connected to MQTT broker %s:%s", self.host, self.port)
        except MqttError as e:
            logger.exception("Failed to connect to MQTT broker")
            raise e

    async def disconnect(self) -> None:
        if self._client is None or not self._connected:
            return
        try:
            await self._client.__aexit__(None, None, None)
            self._connected = False
            logger.info("Disconnected from MQTT broker")
        except Exception:
            logger.exception("Error while disconnecting MQTT client")

    async def publish(self, topic: str, payload: dict) -> None:
        if not self._client or not self._connected:
            raise RuntimeError("MQTT client not connected")
        try:
            await self._client.publish(topic, json.dumps(payload).encode())
            logger.debug("Published to %s: %s", topic, payload)
        except Exception:
            logger.exception("Failed to publish to %s", topic)

    async def publish_activate(self) -> None:
        await self.publish("gym/assist/activate", {"command": "activate"})

    async def publish_disable(self) -> None:
        await self.publish("gym/assist/disable", {"command": "disable"})

    async def listen(self, handlers) -> None:
        """
        Subscribe to decision topics and dispatch messages to handler methods.
        Handler is expected to implement: on_repetition, on_fatigue, on_failure
        """
        if not self._client or not self._connected:
            raise RuntimeError("MQTT client not connected")

        topics = ["gym/decision/repetition", "gym/decision/fatigue", "gym/decision/failure"]
        try:
            messages = self._client.messages

            # subscribe to topics
            for t in topics:
                await self._client.subscribe(t)
                logger.info("Subscribed to %s", t)

            async for msg in messages:
                topic_str = str(msg.topic)
                payload = msg.payload.decode()
                
                # IMPRESIÓN SOLICITADA PARA DEPURACIÓN EN CONSOLA DOCKER
                logger.info("-> [MQTT RECV] Topic: %s | Data: %s", topic_str, payload)
                
                try:
                    data = json.loads(payload)
                except Exception:
                    logger.exception("Invalid JSON payload on %s", topic_str)
                    continue

                # Dispatch by topic
                if topic_str == "gym/decision/repetition":
                    await handlers.on_repetition(data)
                elif topic_str == "gym/decision/fatigue":
                    await handlers.on_fatigue(data)
                elif topic_str == "gym/decision/failure":
                    await handlers.on_failure(data)
        except MqttError:
            logger.exception("MQTT error in listen loop")
            raise
