from __future__ import annotations

from typing import Dict, Any

from app.utils.time import utc_now_iso


def build_state_event(
    state: str,
    rep: int,
    fatigue_score: float,
    confidence: float,
    tracking: bool,
    metrics: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "timestamp": utc_now_iso(),
        "state": state,
        "rep": rep,
        "fatigue_score": round(fatigue_score, 4),
        "confidence": round(confidence, 4),
        "tracking": tracking,
    }
    if metrics is not None:
        payload["metrics"] = metrics
    return payload


def build_repetition_event(rep: int, depth_ok: bool) -> Dict[str, Any]:
    return {
        "timestamp": utc_now_iso(),
        "event": "NEW_REP",
        "rep": rep,
        "depth_ok": depth_ok,
    }


def build_fatigue_event(score: float) -> Dict[str, Any]:
    return {
        "timestamp": utc_now_iso(),
        "fatigue_score": round(score, 4),
    }


def build_failure_event(event: str, confidence: float) -> Dict[str, Any]:
    return {
        "timestamp": utc_now_iso(),
        "event": event,
        "confidence": round(confidence, 4),
    }


def build_metrics_event(metrics: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "timestamp": utc_now_iso(),
        "metrics": metrics,
    }
    return payload


def build_debug_event(debug: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "timestamp": utc_now_iso(),
        "debug": debug,
    }
