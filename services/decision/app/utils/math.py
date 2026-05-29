from __future__ import annotations

import math
from typing import Iterable


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def mean(values: Iterable[float]) -> float | None:
    items = list(values)
    if not items:
        return None
    return sum(items) / len(items)


def std(values: Iterable[float]) -> float | None:
    items = list(values)
    if len(items) < 2:
        return 0.0 if items else None
    avg = sum(items) / len(items)
    variance = sum((item - avg) ** 2 for item in items) / (len(items) - 1)
    return math.sqrt(variance)


def safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0:
        return default
    return numerator / denominator
