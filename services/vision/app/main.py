from __future__ import annotations

import logging
import signal
import time
from typing import Optional

from app.config.settings import Settings
from app.consumers.snapshot_consumer import SnapshotFrameConsumer
from app.consumers.stream_consumer import StreamFrameConsumer
from app.metrics.biomechanics import BiomechanicsCalculator
from app.metrics.internal_metrics import InternalMetrics
from app.mqtt.publisher import MqttPublisher
from app.processing.pipeline import VisionPipeline
from app.providers.mediapipe_pose import MediaPipePoseProvider
from app.schemas.events import build_health_event
from app.services.debug_video import DebugVideoServer
from app.utils.logging import setup_logging
from app.utils.time import utc_now_iso


def _build_consumer(settings: Settings):
    if settings.frame_source == "snapshot":
        return SnapshotFrameConsumer(
            settings.hal_snapshot_url, fps_limit=settings.frame_fps_limit
        )
    return StreamFrameConsumer(settings.hal_stream_url, fps_limit=settings.frame_fps_limit)


def main() -> None:
    settings = Settings.from_env()
    setup_logging(settings.log_level)
    logger = logging.getLogger("vision.main")

    mqtt = MqttPublisher(
        settings.mqtt_host,
        settings.mqtt_port,
        settings.mqtt_username,
        settings.mqtt_password,
    )
    mqtt.connect()

    provider = MediaPipePoseProvider(
        det_conf=settings.pose_det_conf,
        track_conf=settings.pose_track_conf,
        model_path=settings.pose_model_path,
    )
    biomechanics = BiomechanicsCalculator()

    debug_server: Optional[DebugVideoServer] = None
    if settings.debug_video_enable:
        debug_server = DebugVideoServer("0.0.0.0", settings.debug_video_port)
        debug_server.start()
        logger.info("Debug video server enabled on port %s", settings.debug_video_port)

    pipeline = VisionPipeline(provider, biomechanics, debug_server)
    metrics = InternalMetrics()

    consumer = _build_consumer(settings)
    consumer.open()

    stop = False

    def _handle_signal(signum, frame):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    last_metrics_publish = time.monotonic()

    try:
        while not stop:
            packet = consumer.read()
            if packet is None:
                metrics.record_dropped()
                time.sleep(settings.idle_sleep_sec)
                continue

            metrics.record_frame()
            output = pipeline.process_frame(packet.frame_bgr)
            metrics.record_inference(output.inference_sec)
            metrics.set_tracking(output.tracking)
            metrics.set_pipeline_latency_ms(output.pipeline_latency_ms)

            mqtt.publish_json(settings.topic_pose, output.pose_event)
            mqtt.publish_json(settings.topic_metrics, output.metrics_event)

            now = time.monotonic()
            if now - last_metrics_publish >= settings.metrics_interval_sec:
                snapshot = metrics.snapshot()
                payload = build_health_event(
                    timestamp=utc_now_iso(),
                    metrics={
                        "fps": snapshot.fps,
                        "inference_ms_avg": snapshot.inference_ms_avg,
                        "frames_processed": snapshot.frames_processed,
                        "frames_dropped": snapshot.frames_dropped,
                        "tracking": snapshot.tracking,
                        "pipeline_latency_ms": snapshot.last_pipeline_latency_ms,
                    },
                )
                mqtt.publish_json(settings.topic_health, payload)
                last_metrics_publish = now
    finally:
        consumer.close()
        mqtt.close()
        if debug_server is not None:
            debug_server.stop()


if __name__ == "__main__":
    main()
