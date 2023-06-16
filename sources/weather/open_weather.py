"""
OpenWeather API Client
"""
from typing import Literal
import structlog
import httpx

from .models import WeatherData, AirQualityData

UnitType = Literal["standard", "metric", "imperial"]

log = structlog.get_logger()


class OpenWeather:
    """
    Fetching data from OpenWeather's API
    https://openweathermap.org/api
    """

    def __init__(self, token):
        self.token = token
        self.endpoint = "https://api.openweathermap.org/data/2.5/"

    def get_weather(self, town_id: int, units: UnitType) -> WeatherData:
        """
        Get the weather
        """
        params = {
            "id": town_id,
            "units": units,
            "APPID": self.token,
        }
        response = httpx.get(url=self.endpoint + "weather", params=params).json()
        return WeatherData(**response)

    def get_air_quality(self, lat: float, lon: float):
        """
        Get pollution data for a particular latitude / longitude
        """
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.token,
        }
        response = httpx.get(url=self.endpoint + "air_pollution", params=params).json()
        log.info("API Data", data=response)
        return AirQualityData(**response)
