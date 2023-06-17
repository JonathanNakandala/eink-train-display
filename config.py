"""
The configuration for the app

"""
import configparser
from pathlib import Path
from pydantic import BaseSettings


class Tokens(BaseSettings):
    """
    API Tokens
    """

    national_rail: str
    open_weather_map: str


class Stations(BaseSettings):
    """
    Train Stations to query for
    """

    northbound_from: str
    northbound_to: str
    southbound_from: str
    southbound_to: str


class Weather(BaseSettings):
    """
    Openweathermap town
    """

    townid: int


class Config(BaseSettings):
    """
    Application Configuration Class
    """

    tokens: Tokens
    stations: Stations
    weather: Weather


def load_config() -> Config:
    """
    Load and Return the Config from configuration.ini


    """
    config = configparser.ConfigParser()
    config.read(Path(__file__).parent / "configuration.ini")

    # Convert to nested dict
    config_dict = {
        "tokens": dict(config["tokens"]),
        "stations": dict(config["stations"]),
        "weather": {k: int(v) for k, v in config["weather"].items()},
    }

    return Config(**config_dict)
