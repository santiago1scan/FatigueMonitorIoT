from fastapi import APIRouter, Depends, Request, HTTPException
from starlette.status import HTTP_200_OK
import logging

from app.services.assistant_service import AssistantService

router = APIRouter()
logger = logging.getLogger("assist_api.routes")


def get_assistant(request: Request) -> AssistantService:
    svc = getattr(request.app.state, "assistant", None)
    if svc is None:
        raise HTTPException(status_code=500, detail="Assistant service not initialized")
    return svc


@router.post("/assist/start", status_code=HTTP_200_OK)
async def start_assist(assistant: AssistantService = Depends(get_assistant)) -> dict:
    """Activate the HAL assist via MQTT and set active=true."""
    await assistant.start_assist()
    logger.info("Assist started via API")
    return {"active": assistant.active}


@router.post("/assist/stop", status_code=HTTP_200_OK)
async def stop_assist(assistant: AssistantService = Depends(get_assistant)) -> dict:
    """Disable the HAL assist via MQTT and set active=false."""
    await assistant.stop_assist()
    logger.info("Assist stopped via API")
    return {"active": assistant.active}
