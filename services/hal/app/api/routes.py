from __future__ import annotations

from fastapi import APIRouter

from app.schemas.api import ServoTestRequest
from app.services.app_context import AppContext


def build_router(context: AppContext) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health():
        return {"status": "ok"}

    @router.get("/status")
    async def status():
        snapshot = context.build_status()
        return {
            "service": snapshot.service,
            "timestamp": snapshot.timestamp.isoformat(),
            "servo": {"connected": snapshot.servo.connected, "angle": snapshot.servo.angle},
            "camera": {"opened": snapshot.camera.opened},
            "gpio": {
                "configured": snapshot.gpio.configured,
                "last_value": snapshot.gpio.last_value,
            },
            "pwm": {"active": snapshot.pwm.active, "duty_cycle": snapshot.pwm.duty_cycle},
        }

    @router.post("/servo/test")
    async def servo_test(payload: ServoTestRequest):
        await context.servo_service.test_move(payload.angle, payload.force)
        return {"result": "ok"}

    @router.get("/camera/status")
    async def camera_status():
        return {"opened": context.camera_service.opened}

    return router
