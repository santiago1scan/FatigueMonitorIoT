from typing import Set
from fastapi import WebSocket
import logging

from app.models.frontend_state import FrontendState

logger = logging.getLogger("assist_api.websocket")


class ConnectionManager:
    """
    Simple WebSocket connection manager.

    Responsibilities:
    - Track active WebSocket connections
    - Broadcast `FrontendState` updates to all clients

    This class intentionally keeps logic minimal and focused so the
    AssistantService can call `broadcast_state` without depending on
    transport details.
    """

    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.debug("WebSocket connected: %s", websocket.client)

    async def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)
        try:
            await websocket.close()
        except Exception:
            pass
        logger.debug("WebSocket disconnected: %s", websocket.client)

    async def broadcast_state(self, state: FrontendState) -> None:
        payload = state.model_dump_json()
        logger.debug("Broadcasting state to %d clients", len(self.active_connections))
        to_remove = []
        for ws in list(self.active_connections):
            try:
                await ws.send_text(payload)
            except Exception:
                logger.exception("Failed to send to a websocket, scheduling disconnect")
                to_remove.append(ws)
        for ws in to_remove:
            await self.disconnect(ws)
