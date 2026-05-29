from __future__ import annotations

import json
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "decision-service"
    env: str = "dev"
    log_level: str = "INFO"

    mqtt_host: str = "mqtt"
    mqtt_port: int = 1883
    mqtt_username: str | None = None
    mqtt_password: str | None = None
    mqtt_client_id: str = "decision-service"
    mqtt_input_topics: str = "gym/vision/pose,gym/vision/metrics"
    mqtt_topic_state: str = "gym/decision/state"
    mqtt_topic_repetition: str = "gym/decision/repetition"
    mqtt_topic_fatigue: str = "gym/decision/fatigue"
    mqtt_topic_failure: str = "gym/decision/failure"
    mqtt_topic_metrics: str = "gym/decision/metrics"
    mqtt_topic_debug: str = "gym/decision/debug"
    mqtt_health_interval_s: int = 5

    queue_max_size: int = 200
    buffer_size: int = 30

    tuning_enabled: bool = True
    tuning_window_size: int = 200
    tuning_min_samples: int = 40

    smoothing_alpha_angles: float = 0.2
    smoothing_alpha_velocity: float = 0.3
    smoothing_alpha_back: float = 0.2
    smoothing_alpha_positions: float = 0.2

    min_confidence_unstable: float = 0.5
    min_confidence_lost: float = 0.2

    standing_knee_angle_min: float = 165.0
    bottom_knee_angle_max: float = 100.0
    knee_hysteresis_deg: float = 4.0
    vel_descend_threshold: float = -0.05
    vel_ascend_threshold: float = 0.05
    vel_idle_threshold: float = 0.02
    min_confirm_frames: int = 3

    min_rep_interval_s: float = 1.0
    depth_score_min: float = 0.8

    stability_std_max: float = 10.0
    consistency_cv_max: float = 0.25

    baseline_reps: int = 3
    fatigue_weight_velocity: float = 0.4
    fatigue_weight_back: float = 0.2
    fatigue_weight_asymmetry: float = 0.2
    fatigue_weight_stability: float = 0.2
    fatigue_score_smoothing: float = 0.2

    near_failure_velocity_abs: float = 0.03
    near_failure_sticking_s: float = 1.2
    failure_sticking_s: float = 2.5

    def mqtt_input_topics_list(self) -> List[str]:
        raw = self.mqtt_input_topics
        if isinstance(raw, list):
            return [str(item).strip() for item in raw if str(item).strip()]
        raw = raw.strip()
        if not raw:
            return []
        if raw.startswith("["):
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in raw.split(",") if item.strip()]

    class Config:
        env_prefix = "DECISION_"
        case_sensitive = False
