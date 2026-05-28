from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

import numpy as np


@dataclass
class FramePacket:
    frame_bgr: np.ndarray
    timestamp: float


class FrameConsumer(Protocol):
    def open(self) -> None:
        ...

    def read(self) -> Optional[FramePacket]:
        ...

    def close(self) -> None:
        ...
