from typing import Optional
import logging

from app.websocket.connection_manager import ConnectionManager
from app.mqtt.mqtt_client import MQTTClient
from app.models.frontend_state import FrontendState, FatigueFlags
from app.models.repetition import RepetitionEvent
from app.models.fatigue import FatigueEvent
from app.models.failure import FailureEvent

logger = logging.getLogger("assist_api.service")


class AssistantService:
    """
    Business logic for the Assist API.

    Responsibilities:
    - Maintain in-memory session state
    - Convert incoming MQTT events into domain updates
    - Publish commands to HAL via MQTT
    - Broadcast FrontendState via ConnectionManager

    The service is intentionally simple and focuses on one responsibility
    to keep the core logic testable and separate from transport layers.
    """

    def __init__(self, mqtt_client: MQTTClient, connection_manager: ConnectionManager) -> None:
        self._mqtt = mqtt_client
        self._ws = connection_manager

        # In-memory state
        self.repetitions: int = 0
        self.fatigue_score: Optional[float] = None
        self.play_sound: bool = False
        self.active: bool = False

    # --- Public API used by MQTT handlers and HTTP routes ---
    async def process_repetition(self, event: RepetitionEvent) -> None:
        # Update repetitions and broadcast new state
        self.repetitions = event.rep
        logger.info("Processed repetition: %s", event.rep)
        await self._broadcast()

    async def process_fatigue(self, event: FatigueEvent) -> None:
        self.fatigue_score = event.fatigue_score
        logger.info("Processed fatigue score: %s", event.fatigue_score)
        await self._broadcast()

    async def process_failure(self, event: FailureEvent) -> None:
        logger.info("Processed failure event: %s", event.event)
        if event.event == "NEAR_FAILURE":
            self.fatigue_score = 1.0
            await self._broadcast()
        elif event.event == "FAILURE_DETECTED":
            self.fatigue_score = 1.0
            self.play_sound = True
            await self._broadcast()

    async def start_assist(self) -> None:
        # publish and set active
        await self._mqtt.publish_activate()
        self.active = True
        logger.info("Assist activated")
        await self._broadcast()

    async def stop_assist(self) -> None:
        await self._mqtt.publish_disable()
        self.active = False
        logger.info("Assist deactivated")
        await self._broadcast()

    # --- Internal helpers ---
    def _compute_fatigue_flags(self) -> FatigueFlags:
        score = self.fatigue_score if self.fatigue_score is not None else 0.0
        green = score < 0.40
        yellow = 0.40 <= score < 0.75
        red = score >= 0.75
        return FatigueFlags(green=green, yellow=yellow, red=red)

    async def _broadcast(self) -> None:
        state = FrontendState(
            repetitions=self.repetitions,
            fatigue_score=self.fatigue_score if self.fatigue_score is not None else 0.0,
            fatigue=self._compute_fatigue_flags(),
            play_sound=self.play_sound,
            active=self.active,
        )
        try:
            await self._ws.broadcast_state(state)
        finally:
            # After broadcasting the play_sound, reset it so frontend can
            # trigger a single-shot audio event.
            if self.play_sound:
                self.play_sound = False
