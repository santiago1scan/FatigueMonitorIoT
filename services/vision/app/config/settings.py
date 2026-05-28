from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Optional


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name, default)


def _get_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    env: str
    log_level: str

    mqtt_host: str
    mqtt_port: int
    mqtt_username: Optional[str]
    mqtt_password: Optional[str]

    frame_source: str
    hal_stream_url: str
    hal_snapshot_url: str
    frame_fps_limit: float

    pose_det_conf: float
    pose_track_conf: float
    pose_model_path: str

    metrics_interval_sec: int

    debug_video_enable: bool
    debug_video_port: int

    topic_pose: str
    topic_metrics: str
    topic_debug: str
    topic_health: str

    idle_sleep_sec: float

    @staticmethod
    def from_env() -> "Settings":
        return Settings(
            env=_get_env("VISION_ENV", "dev") or "dev",
            log_level=_get_env("VISION_LOG_LEVEL", "INFO") or "INFO",
            mqtt_host=_get_env("VISION_MQTT_HOST", "mqtt") or "mqtt",
            mqtt_port=_get_int("VISION_MQTT_PORT", 1883),
            mqtt_username=_get_env("VISION_MQTT_USERNAME"),
            mqtt_password=_get_env("VISION_MQTT_PASSWORD"),
            frame_source=_get_env("VISION_FRAME_SOURCE", "stream") or "stream",
            hal_stream_url=_get_env(
                "VISION_HAL_STREAM_URL", "http://hal:8080/camera/stream"
            )
            or "http://hal:8080/camera/stream",
            hal_snapshot_url=_get_env(
                "VISION_HAL_SNAPSHOT_URL", "http://hal:8080/camera/frame"
            )
            or "http://hal:8080/camera/frame",
            frame_fps_limit=_get_float("VISION_FRAME_FPS_LIMIT", 0.0),
            pose_det_conf=_get_float("VISION_POSE_DET_CONF", 0.5),
            pose_track_conf=_get_float("VISION_POSE_TRACK_CONF", 0.5),
            pose_model_path=_get_env(
                "VISION_POSE_MODEL_PATH", "pose_landmarker.task"
            )
            or "pose_landmarker.task",
            metrics_interval_sec=_get_int("VISION_METRICS_INTERVAL_SEC", 5),
            debug_video_enable=_get_bool("VISION_DEBUG_VIDEO_ENABLE", False),
            debug_video_port=_get_int("VISION_DEBUG_VIDEO_PORT", 8090),
            topic_pose=_get_env("VISION_TOPIC_POSE", "gym/vision/pose")
            or "gym/vision/pose",
            topic_metrics=_get_env("VISION_TOPIC_METRICS", "gym/vision/metrics")
            or "gym/vision/metrics",
            topic_debug=_get_env("VISION_TOPIC_DEBUG", "gym/vision/debug")
            or "gym/vision/debug",
            topic_health=_get_env("VISION_TOPIC_HEALTH", "gym/vision/health")
            or "gym/vision/health",
            idle_sleep_sec=_get_float("VISION_IDLE_SLEEP_SEC", 0.02),
        )
