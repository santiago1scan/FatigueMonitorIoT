import logging
from typing import Any

from app.models.repetition import RepetitionEvent
from app.models.fatigue import FatigueEvent
from app.models.failure import FailureEvent

logger = logging.getLogger("assist_api.mqtt.handlers")


class MQTTHandlers:
    """
    Adapts raw MQTT JSON payloads to domain models and calls
    business logic in the AssistantService.
    """

    def __init__(self, assistant) -> None:
        self.assistant = assistant

    async def on_repetition(self, data: Any) -> None:
        try:
            event = RepetitionEvent.model_validate(data)
        except Exception:
            logger.exception("Invalid repetition payload")
            return
        await self.assistant.process_repetition(event)

    async def on_fatigue(self, data: Any) -> None:
        try:
            event = FatigueEvent.model_validate(data)
        except Exception:
            logger.exception("Invalid fatigue payload")
            return
        await self.assistant.process_fatigue(event)

    async def on_failure(self, data: Any) -> None:
        try:
            event = FailureEvent.model_validate(data)
        except Exception:
            logger.exception("Invalid failure payload")
            return
        await self.assistant.process_failure(event)
