from __future__ import annotations

import json
import logging
from datetime import datetime

from app.schemas.mqtt import AssistActivatePayload, AssistDisablePayload
from app.services.app_context import AppContext


class MqttHandlers:
    def __init__(self, context: AppContext) -> None:
        self._context = context
        self._logger = logging.getLogger(__name__)

    async def handle(self, topic: str, payload: bytes) -> None:
        if topic == "gym/assist/activate":
            await self._handle_activate(payload)
            return
        if topic == "gym/assist/disable":
            await self._handle_disable(payload)
            return

        self._logger.warning("mqtt_unhandled topic=%s", topic)

    async def publish_health(self) -> None:
        status = self._context.build_status()
        await self._context.mqtt_client.publish(
            self._context.settings.mqtt_health_topic,
            {
                "service": status.service,
                "timestamp": status.timestamp.isoformat(),
                "servo": {"connected": status.servo.connected, "angle": status.servo.angle},
                "camera": {"opened": status.camera.opened},
                "gpio": {
                    "configured": status.gpio.configured,
                    "last_value": status.gpio.last_value,
                },
                "pwm": {"active": status.pwm.active, "duty_cycle": status.pwm.duty_cycle},
            },
        )

    async def _handle_activate(self, payload: bytes) -> None:
        data = AssistActivatePayload.model_validate(json.loads(payload.decode("utf-8")))
        await self._context.servo_service.activate(data.force)
        await self._context.gpio_service.set_status_led(True)
        await self._publish_status("assist_activated")

    async def _handle_disable(self, payload: bytes) -> None:
        AssistDisablePayload.model_validate(json.loads(payload.decode("utf-8")))
        await self._context.servo_service.disable()
        await self._context.gpio_service.set_status_led(False)
        await self._publish_status("assist_disabled")

    async def _publish_status(self, event: str) -> None:
        await self._context.mqtt_client.publish(
            self._context.settings.mqtt_status_topic,
            {
                "service": self._context.settings.app_name,
                "event": event,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
