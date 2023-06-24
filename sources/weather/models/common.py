"""
Common Functions
"""
from datetime import datetime

from pydantic import BaseModel


def parse_timestamp(value: int | datetime) -> datetime:
    """
    Convert the unix time to a datetime
    Used to convert sunset, sunrise and current time
    """
    if isinstance(value, datetime):
        return value
    return datetime.fromtimestamp(value)


class Coordinates(BaseModel):
    """
    Coordinates of weather location
    """

    lon: float
    lat: float
