from __future__ import annotations

import asyncio
import json
import logging
from typing import Awaitable, Callable

from aiomqtt import Client, MqttError

from app.config.settings import Settings


MessageHandler = Callable[[str, bytes], Awaitable[None]]


class MqttClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = logging.getLogger("decision.mqtt")
        self._sub_client = Client(
            hostname=settings.mqtt_host,
            port=settings.mqtt_port,
            username=settings.mqtt_username,
            password=settings.mqtt_password,
        )
        self._pub_client = Client(
            hostname=settings.mqtt_host,
            port=settings.mqtt_port,
            username=settings.mqtt_username,
            password=settings.mqtt_password,
        )
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

    async def start(self, handler: MessageHandler) -> None:
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run(handler))
        self._task.add_done_callback(self._log_task_result)

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def publish(self, topic: str, payload: dict) -> None:
        message = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        try:
            async with self._pub_client as client:
                await client.publish(topic, message)
        except MqttError as exc:
            self._logger.error("mqtt_publish_error topic=%s error=%s", topic, exc)

    async def _run(self, handler: MessageHandler) -> None:
        try:
            async with self._sub_client as client:
                for topic in self._settings.mqtt_input_topics_list():
                    await client.subscribe(topic)
                self._logger.info(
                    "mqtt_connected host=%s topics=%s",
                    self._settings.mqtt_host,
                    ",".join(self._settings.mqtt_input_topics_list()),
                )

                async for message in client.messages:
                    try:
                        self._logger.debug("mqtt_message_received topic=%s", message.topic)
                        await handler(str(message.topic), message.payload)
                    except Exception as exc:
                        self._logger.exception("mqtt_handler_error %s", exc)
                    if self._stop_event.is_set():
                        break
        except MqttError as exc:
            self._logger.error("mqtt_error %s", exc)
        except Exception as exc:
            self._logger.exception("mqtt_unexpected_error %s", exc)

    def _log_task_result(self, task: asyncio.Task) -> None:
        if task.cancelled():
            return
        exc = task.exception()
        if exc:
            self._logger.exception("mqtt_task_failed %s", exc)
