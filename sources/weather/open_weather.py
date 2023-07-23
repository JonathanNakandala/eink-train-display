"""
OpenWeather API Client
"""
from typing import Literal
import structlog
import httpx

from .models import WeatherData, AirQualityData

UnitType = Literal["standard", "metric", "imperial"]

log = structlog.get_logger()


class OpenWeatherException(Exception):
    """General exception for OpenWeather operations."""


class OpenWeather:
    """
    Fetching data from OpenWeather's API
    https://openweathermap.org/api
    """

    def __init__(self, token):
        self.token = token
        self.endpoint = "https://api.openweathermap.org/data/2.5/"
        self.client = httpx.AsyncClient()

    async def get_weather(self, town_id: int, units: UnitType) -> WeatherData:
        """
        Get the weather
        """
        params = {
            "id": town_id,
            "units": units,
            "APPID": self.token,
        }
        log.info("Getting Weather Data", location=town_id, units=units)
        response = await self.client.get(url=self.endpoint + "weather", params=params)
        if response.status_code != 200:
            raise OpenWeatherException(
                f"{response.json().get('message')} Code: {response.status_code}"
            )
        response_data = response.json()
        return WeatherData(**response_data)

    async def get_air_quality(self, lat: float, lon: float):
        """
        Get pollution data for a particular latitude / longitude
        """
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.token,
        }
        log.info("Getting Air Quality Data", lat=lat, lon=lon)
        response = await self.client.get(
            url=self.endpoint + "air_pollution", params=params
        )
        if response.status_code != 200:
            raise OpenWeatherException(f"HTTP error: {response.status_code}")
        response_data = response.json()
        log.info("API Data", data=response_data)
        return AirQualityData(**response_data)

    async def close(self):
        """
        Close the client session
        """
        await self.client.aclose()
