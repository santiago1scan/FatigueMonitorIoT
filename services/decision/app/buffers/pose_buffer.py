from __future__ import annotations

from collections import deque
from typing import Deque, Iterable, List, Callable

from app.biomechanics.types import SmoothedFrame


class PoseBuffer:
    def __init__(self, maxlen: int) -> None:
        self._frames: Deque[SmoothedFrame] = deque(maxlen=maxlen)

    @property
    def frames(self) -> Iterable[SmoothedFrame]:
        return list(self._frames)

    def append(self, frame: SmoothedFrame) -> None:
        self._frames.append(frame)

    def latest(self) -> SmoothedFrame | None:
        if not self._frames:
            return None
        return self._frames[-1]

    def series(self, getter: Callable[[SmoothedFrame], float | None]) -> List[float]:
        values: List[float] = []
        for frame in self._frames:
            value = getter(frame)
            if value is None:
                continue
            values.append(float(value))
        return values

    def duration_s(self) -> float:
        if len(self._frames) < 2:
            return 0.0
        return self._frames[-1].received_time - self._frames[0].received_time
