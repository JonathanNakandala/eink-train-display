"""
Scheduler Operations
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from api.dashboard_data import DashboardInputData, RailwayInformation
from api.dependencies import APIConfig, get_apiconfig

from sources import NationalRail, Weather, Daikin

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


@router.get("/get_dashboard_data", response_model=DashboardInputData)
async def get_dashboard_data(
    api_config: APIConfig = Depends(get_apiconfig),
):
    """
    Convert DeparturesResponse to DashboardData's NationalRail object.
    """
    client = Weather.OpenWeather(token=APIConfig().config.tokens.open_weather_map)
    weather = client.get_weather(APIConfig().config.weather.townid, "metric")
    air_quality = client.get_air_quality(lat=weather.coord.lat, lon=weather.coord.lon)
    rail_client = NationalRail.NationalRail(api_config.config.tokens.national_rail)
    northbound_trains = rail_client.get_departures(
        4,
        api_config.config.stations.northbound_from,
        api_config.config.stations.northbound_to,
    )
    southbound_trains = rail_client.get_departures(
        4,
        api_config.config.stations.southbound_from,
        api_config.config.stations.southbound_to,
    )

    aircon_data = []
    for aircon in api_config.config.aircon.endpoints:
        aircon_data.append(Daikin.DaikinClient(aircon).get_daikin_info())

    dashboard_data = DashboardInputData(
        time=datetime.now(),
        rail=RailwayInformation(
            northbound=northbound_trains, southbound=southbound_trains
        ),
        weather=weather,
        air_quality=air_quality,
        aircon=aircon_data,
    )

    return dashboard_data
