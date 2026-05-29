from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Awaitable, Callable

from app.biomechanics.types import PoseFrame
from app.utils.time import utc_now_iso


FrameHandler = Callable[[PoseFrame], Awaitable[None]]


@dataclass
class PoseMeta:
    timestamp: str
    tracking: bool
    confidence: float


class VisionConsumer:
    def __init__(self) -> None:
        self._logger = logging.getLogger("decision.consumer")
        self._last_meta: PoseMeta | None = None
        self._pose_count = 0
        self._metrics_count = 0

    async def handle_message(self, topic: str, payload: bytes, on_frame: FrameHandler) -> None:
        topic = str(topic)
        try:
            data = json.loads(payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._logger.warning("invalid_payload topic=%s error=%s", topic, exc)
            return

        if topic.endswith("/pose"):
            self._store_pose_meta(data)
            self._pose_count += 1
            if self._pose_count % 50 == 0:
                self._logger.info("pose_messages_received count=%s", self._pose_count)
            return

        if topic.endswith("/metrics"):
            frame = self._build_frame(data)
            self._metrics_count += 1
            if self._metrics_count % 50 == 0:
                self._logger.info(
                    "metrics_messages_received count=%s tracking=%s confidence=%.3f",
                    self._metrics_count,
                    frame.tracking,
                    frame.confidence,
                )
            await on_frame(frame)
            return

        self._logger.debug("ignored_topic topic=%s", topic)

    def _store_pose_meta(self, payload: dict) -> None:
        self._last_meta = PoseMeta(
            timestamp=payload.get("timestamp") or utc_now_iso(),
            tracking=bool(payload.get("tracking", False)),
            confidence=float(payload.get("confidence", 0.0)),
        )

    def _build_frame(self, payload: dict) -> PoseFrame:
        meta = self._last_meta
        timestamp = payload.get("timestamp") or (meta.timestamp if meta else utc_now_iso())
        tracking = bool(payload.get("tracking", meta.tracking if meta else False))
        confidence = float(payload.get("confidence", meta.confidence if meta else 0.0))
        angles = payload.get("angles") or {}
        back_inclination = float(payload.get("back_inclination", 0.0))
        velocity = payload.get("velocity") or {}
        velocity_vertical = float(velocity.get("vertical", 0.0))
        positions = payload.get("positions") or {}
        torso_leg_ratio = payload.get("torso_leg_ratio")
        return PoseFrame(
            timestamp=timestamp,
            received_time=time.monotonic(),
            tracking=tracking,
            confidence=confidence,
            angles=angles,
            back_inclination=back_inclination,
            velocity_vertical=velocity_vertical,
            positions=positions,
            torso_leg_ratio=torso_leg_ratio,
        )
