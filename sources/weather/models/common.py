"""
Common Functions
"""
from datetime import datetime

from pydantic import BaseModel


def parse_timestamp(value: int) -> datetime:
    """
    Convert the unix time to a datetime
    Used to convert sunset, sunrise and current time
    """
    return datetime.fromtimestamp(value)


class Coordinates(BaseModel):
    """
    Coordinates of weather location
    """

    lon: float
    lat: float
