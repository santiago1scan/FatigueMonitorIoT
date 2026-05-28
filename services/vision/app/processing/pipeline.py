from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Optional

import cv2

from app.metrics.biomechanics import BiomechanicsCalculator, BiomechanicsMetrics
from app.providers.base import PoseProvider, PoseResult
from app.schemas.events import build_metrics_event, build_pose_event
from app.services.debug_video import DebugVideoServer
from app.utils.time import utc_now_iso


@dataclass
class PipelineOutput:
    pose_event: dict
    metrics_event: dict
    tracking: bool
    inference_sec: float
    pipeline_latency_ms: float


class VisionPipeline:
    def __init__(
        self,
        provider: PoseProvider,
        biomechanics: BiomechanicsCalculator,
        debug_video: Optional[DebugVideoServer],
    ) -> None:
        self._provider = provider
        self._biomechanics = biomechanics
        self._debug_video = debug_video

    def process_frame(self, frame_bgr) -> PipelineOutput:
        pipeline_start = time.monotonic()
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        infer_start = time.monotonic()
        pose_result = self._provider.process(frame_rgb)
        inference_sec = time.monotonic() - infer_start

        if pose_result.tracking:
            metrics = self._biomechanics.compute(pose_result.landmarks, time.time())
        else:
            metrics = BiomechanicsMetrics(
                angles={},
                back_inclination=None,
                torso_leg_ratio=None,
                vertical_velocity=None,
                joint_positions={},
            )

        if self._debug_video is not None:
            annotated = frame_bgr.copy()
            if pose_result.tracking:
                self._provider.draw_landmarks(annotated, pose_result)
            self._draw_metrics_overlay(annotated, metrics, pose_result.tracking)
            self._debug_video.update_frame(annotated)

        timestamp = utc_now_iso()
        pose_event = build_pose_event(
            timestamp=timestamp,
            tracking=pose_result.tracking,
            landmarks=metrics.joint_positions,
            confidence=pose_result.confidence,
            inference_ms=inference_sec * 1000.0,
        )
        metrics_event = build_metrics_event(
            timestamp=timestamp,
            tracking=pose_result.tracking,
            angles=metrics.angles,
            back_inclination=metrics.back_inclination,
            torso_leg_ratio=metrics.torso_leg_ratio,
            vertical_velocity=metrics.vertical_velocity,
            joint_positions=metrics.joint_positions,
        )

        if self._debug_video is not None:
            self._debug_video.update_metrics(
                {
                    "pose": pose_event,
                    "metrics": metrics_event,
                }
            )

        pipeline_latency_ms = (time.monotonic() - pipeline_start) * 1000.0
        return PipelineOutput(
            pose_event=pose_event,
            metrics_event=metrics_event,
            tracking=pose_result.tracking,
            inference_sec=inference_sec,
            pipeline_latency_ms=pipeline_latency_ms,
        )

    def _draw_metrics_overlay(
        self, frame_bgr, metrics: BiomechanicsMetrics, tracking: bool
    ) -> None:
        lines = [
            f"tracking: {tracking}",
            f"knee_l: {self._fmt(metrics.angles.get('left_knee'))}",
            f"knee_r: {self._fmt(metrics.angles.get('right_knee'))}",
            f"hip_l: {self._fmt(metrics.angles.get('left_hip'))}",
            f"hip_r: {self._fmt(metrics.angles.get('right_hip'))}",
            f"back: {self._fmt(metrics.back_inclination)}",
            f"torso/leg: {self._fmt(metrics.torso_leg_ratio)}",
            f"v_y: {self._fmt(metrics.vertical_velocity)}",
        ]
        y = 24
        for line in lines:
            cv2.putText(
                frame_bgr,
                line,
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )
            y += 22

    @staticmethod
    def _fmt(value: Optional[float]) -> str:
        if value is None:
            return "-"
        return f"{value:.2f}"
