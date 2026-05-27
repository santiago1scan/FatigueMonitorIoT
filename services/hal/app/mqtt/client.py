from __future__ import annotations

import asyncio
import json
import logging
from typing import Callable, Awaitable

from aiomqtt import Client, MqttError

from app.config.settings import Settings


MessageHandler = Callable[[str, bytes], Awaitable[None]]


class MqttClient:
    def __init__(self, settings: Settings, handler: MessageHandler) -> None:
        self._settings = settings
        self._handler = handler
        self._logger = logging.getLogger(__name__)
        self._client = Client(
            hostname=settings.mqtt_host,
            port=settings.mqtt_port,
            username=settings.mqtt_username,
            password=settings.mqtt_password,
            client_id=settings.mqtt_client_id,
        )
        self._task: asyncio.Task | None = None
        self._status_task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

    async def start(self, health_cb: Callable[[], Awaitable[None]]) -> None:
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run())
        self._status_task = asyncio.create_task(self._status_loop(health_cb))

    async def stop(self) -> None:
        self._stop_event.set()
        for task in (self._task, self._status_task):
            if task:
                task.cancel()
        for task in (self._task, self._status_task):
            if task:
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    async def publish(self, topic: str, payload: dict) -> None:
        message = json.dumps(payload).encode("utf-8")
        async with self._client as client:
            await client.publish(topic, message)

    async def _status_loop(self, health_cb: Callable[[], Awaitable[None]]) -> None:
        while not self._stop_event.is_set():
            await health_cb()
            await asyncio.sleep(self._settings.mqtt_status_interval_s)

    async def _run(self) -> None:
        try:
            async with self._client as client:
                for topic in self._settings.mqtt_topics:
                    await client.subscribe(topic)
                self._logger.info("mqtt_connected host=%s", self._settings.mqtt_host)

                async with client.unfiltered_messages() as messages:
                    async for message in messages:
                        await self._handler(message.topic, message.payload)
        except MqttError as exc:
            self._logger.error("mqtt_error %s", exc)
