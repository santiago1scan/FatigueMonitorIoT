from __future__ import annotations

from typing import Dict, List, Optional

import mediapipe as mp
import numpy as np
import cv2

from app.providers.base import Landmark, PoseResult, PoseProvider


class MediaPipePoseProvider(PoseProvider):
    def __init__(self, det_conf: float, track_conf: float, model_path: str) -> None:
        self._use_solutions = hasattr(mp, "solutions") and hasattr(mp.solutions, "pose")
        self._mp_pose = None
        self._drawer = None
        self._task_pose = None
        self._task_landmark_enum = None
        self._task_image = None

        if self._use_solutions:
            self._mp_pose = mp.solutions.pose
            self._pose = self._mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                smooth_landmarks=True,
                min_detection_confidence=det_conf,
                min_tracking_confidence=track_conf,
            )
            self._drawer = mp.solutions.drawing_utils
        else:
            from mediapipe.tasks.python.core import base_options
            from mediapipe.tasks.python.vision.core import image as mp_image
            from mediapipe.tasks.python.vision.pose_landmarker import (
                PoseLandmarker,
                PoseLandmarkerOptions,
                PoseLandmark,
            )

            self._task_image = mp_image
            self._task_landmark_enum = PoseLandmark
            base_opts = base_options.BaseOptions(model_asset_path=model_path)
            options = PoseLandmarkerOptions(
                base_options=base_opts,
                min_pose_detection_confidence=det_conf,
                min_pose_presence_confidence=det_conf,
                min_tracking_confidence=track_conf,
            )
            self._task_pose = PoseLandmarker.create_from_options(options)

    def process(self, frame_rgb: np.ndarray) -> PoseResult:
        if self._use_solutions:
            result = self._pose.process(frame_rgb)
            landmarks = result.pose_landmarks.landmark if result.pose_landmarks else None
        else:
            mp_img = self._task_image.Image(
                self._task_image.ImageFormat.SRGB, frame_rgb
            )
            result = self._task_pose.detect(mp_img)
            landmarks = result.pose_landmarks[0] if result.pose_landmarks else None

        if not landmarks:
            return PoseResult(
                landmarks={},
                confidence=0.0,
                tracking=False,
                raw_landmarks=[],
                raw_result=None,
            )

        raw_landmarks = self._convert_landmarks(landmarks)
        named = self._select_landmarks(landmarks)
        confidence = self._estimate_confidence(raw_landmarks)
        return PoseResult(
            landmarks=named,
            confidence=confidence,
            tracking=True,
            raw_landmarks=raw_landmarks,
            raw_result=result,
        )

    def draw_landmarks(self, frame_bgr: np.ndarray, result: PoseResult) -> None:
        if result.raw_result is None:
            return None
        if self._use_solutions and self._drawer and self._mp_pose:
            self._drawer.draw_landmarks(
                frame_bgr,
                result.raw_result.pose_landmarks,
                self._mp_pose.POSE_CONNECTIONS,
            )
            return None
        self._draw_simple_overlay(frame_bgr, result.landmarks)

    def _convert_landmarks(self, landmarks: List[object]) -> List[Landmark]:
        converted: List[Landmark] = []
        for lm in landmarks:
            visibility = getattr(lm, "visibility", getattr(lm, "presence", 1.0))
            converted.append(
                Landmark(x=lm.x, y=lm.y, z=lm.z, visibility=visibility)
            )
        return converted

    def _select_landmarks(self, landmarks: List[object]) -> Dict[str, Landmark]:
        mp_landmark = self._mp_pose.PoseLandmark if self._use_solutions else None
        mapping = {
            "left_shoulder": mp_landmark.LEFT_SHOULDER
            if self._use_solutions
            else self._task_landmark_enum.LEFT_SHOULDER,
            "right_shoulder": mp_landmark.RIGHT_SHOULDER
            if self._use_solutions
            else self._task_landmark_enum.RIGHT_SHOULDER,
            "left_hip": mp_landmark.LEFT_HIP
            if self._use_solutions
            else self._task_landmark_enum.LEFT_HIP,
            "right_hip": mp_landmark.RIGHT_HIP
            if self._use_solutions
            else self._task_landmark_enum.RIGHT_HIP,
            "left_knee": mp_landmark.LEFT_KNEE
            if self._use_solutions
            else self._task_landmark_enum.LEFT_KNEE,
            "right_knee": mp_landmark.RIGHT_KNEE
            if self._use_solutions
            else self._task_landmark_enum.RIGHT_KNEE,
            "left_ankle": mp_landmark.LEFT_ANKLE
            if self._use_solutions
            else self._task_landmark_enum.LEFT_ANKLE,
            "right_ankle": mp_landmark.RIGHT_ANKLE
            if self._use_solutions
            else self._task_landmark_enum.RIGHT_ANKLE,
        }
        named: Dict[str, Landmark] = {}
        for name, idx in mapping.items():
            index = idx.value if hasattr(idx, "value") else int(idx)
            lm = landmarks[index]
            visibility = getattr(lm, "visibility", getattr(lm, "presence", 1.0))
            named[name] = Landmark(x=lm.x, y=lm.y, z=lm.z, visibility=visibility)
        return named

    def _estimate_confidence(self, landmarks: List[Landmark]) -> float:
        if not landmarks:
            return 0.0
        total = sum(lm.visibility for lm in landmarks)
        return total / len(landmarks)

    def _draw_simple_overlay(
        self, frame_bgr: np.ndarray, landmarks: Dict[str, Landmark]
    ) -> None:
        if not landmarks:
            return None
        h, w = frame_bgr.shape[:2]

        def pt(name: str) -> Optional[tuple[int, int]]:
            lm = landmarks.get(name)
            if lm is None:
                return None
            return (int(lm.x * w), int(lm.y * h))

        joints = [
            "left_shoulder",
            "right_shoulder",
            "left_hip",
            "right_hip",
            "left_knee",
            "right_knee",
            "left_ankle",
            "right_ankle",
        ]
        for name in joints:
            point = pt(name)
            if point is not None:
                cv2.circle(frame_bgr, point, 4, (0, 255, 0), -1)

        lines = [
            ("left_shoulder", "left_hip"),
            ("left_hip", "left_knee"),
            ("left_knee", "left_ankle"),
            ("right_shoulder", "right_hip"),
            ("right_hip", "right_knee"),
            ("right_knee", "right_ankle"),
            ("left_shoulder", "right_shoulder"),
            ("left_hip", "right_hip"),
        ]
        for a, b in lines:
            p1 = pt(a)
            p2 = pt(b)
            if p1 is not None and p2 is not None:
                cv2.line(frame_bgr, p1, p2, (0, 255, 0), 2)
