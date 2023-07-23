"""
Scheduler Operations
"""
import asyncio
from datetime import datetime, timedelta
import pytz
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from api.dashboard_data import DashboardInputData, RailwayInformation
from api.dependencies import APIConfig, get_apiconfig
from api.config import AirConConfig, ConfigVars
from sources import NationalRail, Weather, Daikin
from sources.daikin.models import DaikinInfo
from sources.national_rail.models import DeparturesResponse

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


async def get_aircon_data(aircon_config: AirConConfig) -> list[DaikinInfo]:
    """
    Gather the Aircon tasks and run in parallel
    """
    tasks = []
    for aircon in aircon_config.endpoints:
        client = Daikin.DaikinClient(aircon)
        tasks.append(client.get_daikin_info())
    aircon_data: list[DaikinInfo] = await asyncio.gather(*tasks)
    return aircon_data


async def get_rail_data(
    config: ConfigVars,
) -> tuple[DeparturesResponse, DeparturesResponse]:
    """
    Gather the Aircon tasks and run in parallel
    """
    rail_client = NationalRail.NationalRail(config.tokens.national_rail)

    northbound_trains_future = rail_client.get_departures(
        4,
        config.stations.northbound_from,
        config.stations.northbound_to,
    )

    southbound_trains_future = rail_client.get_departures(
        4,
        config.stations.southbound_from,
        config.stations.southbound_to,
    )

    northbound_trains, southbound_trains = await asyncio.gather(
        northbound_trains_future, southbound_trains_future
    )

    return northbound_trains, southbound_trains


async def get_weather_data(client, townid):
    """
    Fetch weather and air quality data asynchronously
    """
    weather = await client.get_weather(townid, "metric")
    air_quality = await client.get_air_quality(
        lat=weather.coord.lat, lon=weather.coord.lon
    )
    return weather, air_quality


@router.get("/get_dashboard_data", response_model=DashboardInputData)
async def get_dashboard_data(
    api_config: APIConfig = Depends(get_apiconfig),
):
    """
    Convert DeparturesResponse to DashboardData's NationalRail object.
    Uses asyncio to fetch in parallel
    """
    client = Weather.OpenWeather(token=APIConfig().config.tokens.open_weather_map)

    weather_data_future = get_weather_data(client, APIConfig().config.weather.townid)
    aircon_data_future = get_aircon_data(api_config.config.aircon)
    rail_data_future = get_rail_data(api_config.config)

    weather_data, aircon_data, rail_data = await asyncio.gather(
        weather_data_future, aircon_data_future, rail_data_future
    )

    weather, air_quality = weather_data
    northbound_trains, southbound_trains = rail_data
    now_utc = datetime.now(pytz.timezone("UTC"))
    now_london = now_utc.astimezone(pytz.timezone("Europe/London"))

    dashboard_data = DashboardInputData(
        time=now_london,
        rail=RailwayInformation(
            northbound=northbound_trains, southbound=southbound_trains
        ),
        weather=weather,
        air_quality=air_quality,
        aircon=aircon_data,
    )

    return dashboard_data
