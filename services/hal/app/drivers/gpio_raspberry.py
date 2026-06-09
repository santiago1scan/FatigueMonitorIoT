from __future__ import annotations

import logging
import mmap
import os
import struct

from app.config.settings import Settings
from app.domain.base import BaseGPIO

GPIO_BASE = 0x200000

GPFSEL = [0x00, 0x04, 0x08, 0x0c, 0x10, 0x14]
GPSET = [0x1c, 0x20]
GPCLR = [0x28, 0x2c]


class RaspberryGPIO(BaseGPIO):
    def __init__(self, settings: Settings) -> None:
        self._logger = logging.getLogger(__name__)
        self._map: mmap.mmap | None = None

    async def setup_output(self, pin: int) -> None:
        fd = os.open("/dev/gpiomem", os.O_RDWR | os.O_SYNC)
        self._map = mmap.mmap(fd, 0x1000, offset=GPIO_BASE)
        os.close(fd)

        reg_idx = pin // 10
        bit_shift = (pin % 10) * 3

        raw = self._read32(GPFSEL[reg_idx])
        raw &= ~(7 << bit_shift)
        raw |= 1 << bit_shift
        self._write32(GPFSEL[reg_idx], raw)

        self._logger.info("raspberry_gpio_setup pin=%s", pin)

    async def write(self, pin: int, value: bool) -> None:
        if not self._map:
            raise RuntimeError("gpio_not_configured")
        if value:
            self._write32(GPSET[pin // 32], 1 << (pin % 32))
        else:
            self._write32(GPCLR[pin // 32], 1 << (pin % 32))
        self._logger.info("raspberry_gpio_write pin=%s value=%s", pin, value)

    def _read32(self, offset: int) -> int:
        return struct.unpack("<I", self._map[offset : offset + 4])[0]

    def _write32(self, offset: int, value: int) -> None:
        self._map[offset : offset + 4] = struct.pack("<I", value)
