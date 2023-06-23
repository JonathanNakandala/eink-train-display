"""
Scheduler Operations
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from api.dependencies import APIConfig, get_apiconfig

router = APIRouter()


class UpdateConfigBody(BaseModel):
    """
    Pydantic Model for API Config
    """

    interval_minutes: int


@router.post("/schedule/update")
async def update_dashboard(
    request: Request, api_config: APIConfig = Depends(get_apiconfig)
):
    """
    Endpoint to manually trigger the dashboard update
    """
    api_config.update_now(request)
    return {"message": "Dashboard update scheduled"}


@router.post("/schedule/config")
async def update_config(
    request: Request,
    new_config: UpdateConfigBody,
    api_config: APIConfig = Depends(get_apiconfig),
):
    """
    Endpoint to update the dashboard update frequency
    """
    current_interval = api_config.update_interval
    new_interval = timedelta(minutes=new_config.interval_minutes)
    api_config.reschedule(request, new_interval)
    api_config.update_interval = timedelta(minutes=new_config.interval_minutes)
    return {
        "message": "Dashboard update frequency updated",
        "current_interval": current_interval,
        "new_interval": new_config.interval_minutes,
    }
