from __future__ import annotations

import asyncio
import logging

from app.config.settings import Settings
from app.domain.base import BaseGPIO


class GPIOService:
    def __init__(self, driver: BaseGPIO, settings: Settings) -> None:
        self._driver = driver
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self.configured = False
        self.last_value: bool | None = None
        self._blink_task: asyncio.Task | None = None

    async def configure(self) -> None:
        await self._driver.setup_output(self._settings.status_led_pin)
        self.configured = True
        await self.set_status_led(False)

    async def set_status_led(self, enabled: bool) -> None:
        await self._driver.write(self._settings.status_led_pin, enabled)
        self.last_value = enabled
        self._logger.info("gpio_write pin=%s value=%s", self._settings.status_led_pin, enabled)

    async def start_blink(self, interval: float = 0.5) -> None:
        await self.stop_blink()
        self._blink_task = asyncio.create_task(self._blink_loop(interval))

    async def stop_blink(self) -> None:
        if self._blink_task:
            self._blink_task.cancel()
            try:
                await self._blink_task
            except asyncio.CancelledError:
                pass
            self._blink_task = None

    async def _blink_loop(self, interval: float) -> None:
        while True:
            await self.set_status_led(True)
            await asyncio.sleep(interval)
            await self.set_status_led(False)
            await asyncio.sleep(interval)

    async def shutdown(self) -> None:
        if self.configured:
            await self.stop_blink()
            await self.set_status_led(False)
            self.configured = False
