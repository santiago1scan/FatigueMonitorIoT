from __future__ import annotations

import json
import logging
from typing import Optional

import paho.mqtt.client as mqtt


class MqttPublisher:
    def __init__(self, host: str, port: int, username: Optional[str], password: Optional[str]):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._client = mqtt.Client()
        self._logger = logging.getLogger("vision.mqtt")

    def connect(self) -> None:
        if self._username and self._password:
            self._client.username_pw_set(self._username, self._password)
        self._client.connect(self._host, self._port, keepalive=30)
        self._client.loop_start()

    def publish_json(self, topic: str, payload: dict) -> None:
        try:
            message = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
            self._client.publish(topic, message, qos=0)
        except (TypeError, ValueError) as exc:
            self._logger.error("Failed to publish payload: %s", exc)

    def close(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()
