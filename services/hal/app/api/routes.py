from __future__ import annotations

import asyncio

from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse

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
            "camera": {"opened": snapshot.camera.opened},
            "gpio": {
                "configured": snapshot.gpio.configured,
                "last_value": snapshot.gpio.last_value,
            },
        }

    @router.get("/camera/status")
    async def camera_status():
        return {"opened": context.camera_service.opened}

    @router.get("/camera/frame")
    async def camera_frame():
        frame = await context.camera_service.get_frame()
        if not frame:
            return Response(status_code=204)
        return Response(content=frame, media_type="image/jpeg")

    @router.get("/camera/stream")
    async def camera_stream():
        async def mjpeg_stream():
            while True:
                frame = await context.camera_service.get_frame()
                if frame:
                    header = (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n"
                        + f"Content-Length: {len(frame)}\r\n\r\n".encode("ascii")
                    )
                    yield header + frame + b"\r\n"
                await asyncio.sleep(0.05)

        return StreamingResponse(
            mjpeg_stream(),
            media_type="multipart/x-mixed-replace; boundary=frame",
        )

    return router
