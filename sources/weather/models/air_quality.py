"""
Air quality from Openweather map
https://openweathermap.org/api/air-pollution

"""
from datetime import datetime

from pydantic import BaseModel, Field, validator

from .common import Coordinates, parse_timestamp


class Components(BaseModel):
    """
    Concentrations of various air pollutants.
    """

    co: float = Field(
        ...,
        description="""
        Сoncentration of CO (Carbon monoxide), μg/m3
        """,
    )
    no: float = Field(
        ...,
        description="""
        Сoncentration of NO (Nitrogen monoxide), μg/m3
        """,
    )
    no2: float = Field(
        ...,
        description="""
        Сoncentration of NO2 (Nitrogen dioxide), μg/m3
        """,
    )
    o3: float = Field(
        ...,
        description="""
        Сoncentration of O3 (Ozone), μg/m3
        """,
    )
    so2: float = Field(
        ...,
        description="""
        Сoncentration of SO2 (Sulphur dioxide), μg/m3
        """,
    )
    pm2_5: float = Field(
        ...,
        description="""
        Сoncentration of PM2.5 (Fine particles matter), μg/m3
        """,
    )
    pm10: float = Field(
        ...,
        description="""
        Сoncentration of PM10 (Coarse particulate matter), μg/m3
        """,
    )
    nh3: float = Field(
        ...,
        description="""
        Сoncentration of NH3 (Ammonia), μg/m3
        """,
    )


class Main(BaseModel):
    """
    Air quality index data.
    """

    aqi: int = Field(
        ...,
        description="""
        Air Quality Index. Possible values: 1, 2, 3, 4, 5. 
        Where 1 = Good, 2 = Fair, 3 = Moderate, 4 = Poor, 5 = Very Poor.
        """,
    )


class ListElement(BaseModel):
    """
    Air quality and components for a given timestamp.
    """

    dt: datetime = Field(..., description="Date and time, Unix, UTC")
    main: Main
    components: Components

    _set_timestamp: classmethod = validator("dt", pre=True, allow_reuse=True)(
        parse_timestamp
    )


class AirQualityData(BaseModel):
    """
    Air quality data for a specific location.
    """

    coord: Coordinates = Field(
        ..., description="Coordinates from the specified location (latitude, longitude)"
    )
    list: list[ListElement]
