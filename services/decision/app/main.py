from __future__ import annotations

import asyncio
import logging
import signal
import time
from typing import Any, Dict

from app.biomechanics.features import compute_features
from app.biomechanics.tuning import ThresholdTuner
from app.buffers.pose_buffer import PoseBuffer
from app.config.settings import Settings
from app.consumers.vision_consumer import VisionConsumer
from app.failure_detection.detector import FailureDetector
from app.fatigue.estimator import FatigueEstimator
from app.metrics.internal_metrics import InternalMetrics
from app.mqtt.client import MqttClient
from app.schemas.events import (
    build_debug_event,
    build_failure_event,
    build_fatigue_event,
    build_metrics_event,
    build_repetition_event,
    build_state_event,
)
from app.smoothing.ema import EmaSmoother
from app.state_machine.machine import BiomechStateMachine
from app.state_machine.repetition import RepCounter
from app.state_machine.states import BiomechState
from app.utils.logging import setup_logging


def _compact_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in metrics.items() if value is not None}


async def _run() -> None:
    settings = Settings()
    setup_logging(settings.log_level)
    logger = logging.getLogger("decision.main")

    queue: asyncio.Queue = asyncio.Queue(maxsize=settings.queue_max_size)
    buffer = PoseBuffer(settings.buffer_size)
    smoother = EmaSmoother(settings)
    consumer = VisionConsumer()
    state_machine = BiomechStateMachine(settings)
    rep_counter = RepCounter(settings)
    fatigue = FatigueEstimator(settings)
    failure_detector = FailureDetector(settings)
    tuner = ThresholdTuner(settings)
    internal_metrics = InternalMetrics()

    mqtt = MqttClient(settings)
    stop_event = asyncio.Event()

    def _handle_signal(signum, frame) -> None:
        stop_event.set()

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    async def on_frame(frame) -> None:
        internal_metrics.record_received()
        try:
            queue.put_nowait(frame)
        except asyncio.QueueFull:
            internal_metrics.record_dropped()

    async def handle_message(topic: str, payload: bytes) -> None:
        await consumer.handle_message(topic, payload, on_frame)

    await mqtt.start(handle_message)

    last_metrics_publish = time.monotonic()
    last_debug_publish = time.monotonic()
    processed_count = 0
    last_frame_time = time.monotonic()

    try:
        while not stop_event.is_set():
            try:
                frame = await asyncio.wait_for(queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                frame = None

            if frame is None:
                now = time.monotonic()
                if now - last_debug_publish >= settings.mqtt_health_interval_s:
                    snapshot = internal_metrics.snapshot()
                    debug_payload = build_debug_event(
                        {
                            "frames_received": snapshot.frames_received,
                            "frames_processed": snapshot.frames_processed,
                            "frames_invalid": snapshot.frames_invalid,
                            "frames_dropped": snapshot.frames_dropped,
                            "state_transitions": snapshot.state_transitions,
                            "last_processing_ms": snapshot.last_processing_ms,
                            "queue_size": snapshot.queue_size,
                            "current_state": state_machine.state.value,
                            "seconds_since_last_frame": round(now - last_frame_time, 3),
                        }
                    )
                    await mqtt.publish(settings.mqtt_topic_debug, debug_payload)
                    last_debug_publish = now
                continue

            start = time.monotonic()
            last_frame_time = start

            if not frame.tracking or frame.confidence < settings.min_confidence_lost:
                internal_metrics.record_invalid()

            smoothed = smoother.update(frame)
            buffer.append(smoothed)
            features = compute_features(smoothed, buffer, settings)

            state_update = state_machine.update(features, smoothed)
            if state_update.changed:
                internal_metrics.record_transition()

            tuner.update(state_update.state, features)

            rep_event = rep_counter.update(state_update, features)
            fatigue_score = fatigue.update(features, state_update, rep_event)
            failure_event = failure_detector.update(features, state_update)
            if failure_event and failure_event.event == "FAILURE_DETECTED":
                state_update = state_machine.force_state(
                    BiomechState.FAILED_REP, state_update.confidence
                )

            internal_metrics.record_processed(
                (time.monotonic() - start) * 1000.0,
                queue.qsize(),
            )
            processed_count += 1
            if processed_count % 50 == 0:
                logger.info(
                    "frames_processed count=%s state=%s rep=%s",
                    processed_count,
                    state_update.state.value,
                    rep_counter.rep_count,
                )

            metrics_payload = _compact_metrics(
                {
                    "knee_angle_avg": features.knee_angle_avg,
                    "hip_angle_avg": features.hip_angle_avg,
                    "knee_asymmetry": features.knee_asymmetry,
                    "back_inclination": features.back_inclination,
                    "velocity_vertical": features.velocity_vertical,
                    "depth_score": features.depth_score,
                    "stability": features.stability,
                    "consistency": features.consistency,
                }
            )

            state_payload = build_state_event(
                state_update.state.value,
                rep_counter.rep_count,
                fatigue_score,
                state_update.confidence,
                smoothed.tracking,
                metrics_payload,
            )
            await mqtt.publish(settings.mqtt_topic_state, state_payload)

            await mqtt.publish(settings.mqtt_topic_fatigue, build_fatigue_event(fatigue_score))

            if rep_event:
                rep_payload = build_repetition_event(rep_event.rep_count, rep_event.depth_ok)
                await mqtt.publish(settings.mqtt_topic_repetition, rep_payload)

            if failure_event:
                failure_payload = build_failure_event(failure_event.event, failure_event.confidence)
                await mqtt.publish(settings.mqtt_topic_failure, failure_payload)

            now = time.monotonic()
            if now - last_metrics_publish >= settings.mqtt_health_interval_s:
                await mqtt.publish(settings.mqtt_topic_metrics, build_metrics_event(metrics_payload))
                last_metrics_publish = now

            if now - last_debug_publish >= settings.mqtt_health_interval_s:
                snapshot = internal_metrics.snapshot()
                tuning = tuner.suggestions()
                debug_payload = build_debug_event(
                    {
                        "frames_received": snapshot.frames_received,
                        "frames_processed": snapshot.frames_processed,
                        "frames_invalid": snapshot.frames_invalid,
                        "frames_dropped": snapshot.frames_dropped,
                        "state_transitions": snapshot.state_transitions,
                        "last_processing_ms": snapshot.last_processing_ms,
                        "queue_size": snapshot.queue_size,
                        "current_state": state_update.state.value,
                        "seconds_since_last_frame": round(now - last_frame_time, 3),
                        "tuning_suggestions": tuning.__dict__ if tuning else None,
                    }
                )
                await mqtt.publish(settings.mqtt_topic_debug, debug_payload)
                last_debug_publish = now

    except asyncio.CancelledError:
        logger.info("decision_loop_cancelled")
    finally:
        await mqtt.stop()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
