"""
Generate Data for Svelte
"""
from datetime import datetime
from pydantic import BaseModel
from sources.national_rail.models import DeparturesResponse
from sources.weather.models import AirQualityData, WeatherData
from sources.daikin.models import DaikinInfo


class RailwayInformation(BaseModel):
    """
    Railway Information
    """

    northbound: DeparturesResponse
    southbound: DeparturesResponse


class DashboardInputData(BaseModel):
    """
    Data for Dashboard
    """

    rail: RailwayInformation
    weather: WeatherData
    time: datetime
    air_quality: AirQualityData
    aircon: list[DaikinInfo]
