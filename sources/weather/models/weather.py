"""
OpenWeatherAPI Models
https://openweathermap.org/api/one-call-3
"""
from datetime import datetime
from pydantic import BaseModel, validator

from .common import parse_timestamp, Coordinates


class Weather(BaseModel):
    """
    The description of the weather e.g. Clouds
    """

    id: int
    main: str
    description: str
    icon: str


class Main(BaseModel):
    """
    The section with the values
    """

    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int


class Wind(BaseModel):
    """
    Wind speed and direction
    """

    speed: float
    deg: int


class Clouds(BaseModel):
    """
    Not sure
    """

    all: int


class Sys(BaseModel):
    """
    Extra info
    """

    type: int
    id: int
    country: str
    sunrise: datetime
    sunset: datetime

    _set_timestamp: classmethod = validator(
        "sunset", "sunrise", pre=True, allow_reuse=True
    )(parse_timestamp)


class WeatherData(BaseModel):
    """
    API Response Data
    """

    coord: Coordinates
    weather: list[Weather]
    base: str
    main: Main
    visibility: int
    wind: Wind
    clouds: Clouds
    dt: datetime
    sys: Sys
    timezone: int
    id: int
    name: str
    cod: int

    _set_timestamp: classmethod = validator("dt", pre=True, allow_reuse=True)(
        parse_timestamp
    )
