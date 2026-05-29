from __future__ import annotations

from enum import Enum


class BiomechState(str, Enum):
    IDLE = "IDLE"
    STANDING = "STANDING"
    DESCENDING = "DESCENDING"
    BOTTOM = "BOTTOM"
    ASCENDING = "ASCENDING"
    LOCKOUT = "LOCKOUT"
    FAILED_REP = "FAILED_REP"
    TRACKING_LOST = "TRACKING_LOST"
    TRACKING_UNSTABLE = "TRACKING_UNSTABLE"
