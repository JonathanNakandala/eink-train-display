"""
Generate Data for Svelte
"""
from datetime import datetime
from pydantic import BaseModel
from sources.national_rail.models import DeparturesResponse

from sources.weather.models.weather import WeatherData


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
