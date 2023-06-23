"""
Image Generation and sending to Display
"""

import datetime

import httpx
import structlog
from fastapi import HTTPException
from PIL import Image
from api.dependencies import APIConfig

from render import Pillow
from sources import NationalRail, Weather
from waveshare_epd import epd7in5_V2


log = structlog.get_logger()


def send_to_server(pil_image: Image):
    """
    Send to a server
    """
    # Define the API endpoint URL
    url = APIConfig().config.endpoints.display_server
    epd = epd7in5_V2.EPD()
    data_bytes = bytes(epd.getbuffer(pil_image))

    # Send the bytes to the API
    headers = {"Content-Type": "application/octet-stream"}
    response = httpx.post(url, content=data_bytes, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        file_size = response_data.get("file_size")
        log.info(f"File size: {file_size} bytes")
    else:
        raise HTTPException(
            status_code=500, detail="Failed to send the bytearray to the server"
        )


def is_within_update_hours():
    """
    Don't need to update in middle of night
    """
    dashboard_update_enabled_hours = (6, 24)
    now = datetime.datetime.now()
    return (
        dashboard_update_enabled_hours[0]
        <= now.hour
        < dashboard_update_enabled_hours[1]
    )


def round_number_to_string(number: int) -> str:
    """Round an int and convert to string"""
    return str(int(round(number)))


def get_weather():
    """
    Get Weather from Open Weather Map API
    """
    client = Weather.OpenWeather(token=APIConfig().config.tokens.open_weather_map)
    data = client.get_weather(APIConfig().config.weather.townid, "metric")
    temp = {
        "Average": round_number_to_string(data.main.temp),
        "High": round_number_to_string(data.main.temp_max),
        "Low": round_number_to_string(data.main.temp_min),
        "Weather": data.weather[0].main,
    }
    return temp


def run_dashboard_update(api_config: APIConfig):
    """
    Run dashboard update if between two hours
    """
    if not is_within_update_hours():
        log.info("Dashboard update disabled at this hour")
        return
    rail_client = NationalRail.NationalRail(api_config.config.tokens.national_rail)
    pil_image = Pillow.render_pillow_dashboard(
        rail_nb=rail_client.get_departures(
            4,
            api_config.config.stations.northbound_from,
            api_config.config.stations.northbound_to,
        ),
        rail_sb=rail_client.get_departures(
            4,
            api_config.config.stations.southbound_from,
            api_config.config.stations.southbound_to,
        ),
        temperature_data=get_weather(),
    )

    log.info("Displaying image and saving preview.png")
    pil_image.save("preview.png")
    # send_to_display(pil_image)
    send_to_server(pil_image)
