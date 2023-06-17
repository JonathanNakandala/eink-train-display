"""
Home Dashboard for a WaveShare 7.5 e-ink display with Raspberry PI
"""
import sys
import datetime

import httpx
import structlog
from PIL import Image
import uvicorn
from pydantic import BaseModel
from fastapi import Depends, FastAPI, BackgroundTasks, HTTPException

from sources import NationalRail, Weather
from render import Pillow
from waveshare_epd import epd7in5_V2, epdconfig

from config import load_config

log = structlog.get_logger()

config = load_config()

app = FastAPI()

dashboard_update_interval = datetime.timedelta(minutes=5)
dashboard_update_enabled_hours = (6, 24)  # Update enabled between 6 AM and 11 PM


class APIConfig:
    """
    Singleton for API Configuration
    """

    _instance = None
    update_interval: datetime.timedelta = datetime.timedelta(minutes=5)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(APIConfig, cls).__new__(cls)
        return cls._instance


def get_apiconfig():
    """
    Returns APIConfig for use in Depends
    """
    return APIConfig()


class UpdateConfig(BaseModel):
    """
    Pydantic Model for API Config
    """

    interval_minutes: int


def round_number_to_string(number: int) -> str:
    """Round an int and convert to string"""
    return str(int(round(number)))


def get_weather():
    """
    Get Weather from Open Weather Map API
    """
    client = Weather.OpenWeather(token=config.tokens.open_weather_map)
    data = client.get_weather(config.weather.townid, "metric")
    temp = {
        "Average": round_number_to_string(data.main.temp),
        "High": round_number_to_string(data.main.temp_max),
        "Low": round_number_to_string(data.main.temp_min),
        "Weather": data.weather[0].main,
    }
    return temp


def send_to_display(pil_image: Image):
    """
    Send Data to Display
    """
    epd = epd7in5_V2.EPD()
    log.info("Initializing the display...")
    epd.init()
    epd.display(epd.getbuffer(pil_image))
    log.info("Sending Display to Sleep")
    epd.sleep()


def send_to_server(pil_image: Image):
    """
    Send to a server
    """
    # Define the API endpoint URL
    url = "http://192.168.0.50:8000/upload"
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
    now = datetime.datetime.now()
    return (
        dashboard_update_enabled_hours[0]
        <= now.hour
        < dashboard_update_enabled_hours[1]
    )


def run_dashboard_update():
    """
    Run dashboard update if between two hours
    """
    if not is_within_update_hours():
        log.info("Dashboard update disabled at this hour")
        return
    rail_client = NationalRail.NationalRail(config.tokens.national_rail)
    pil_image = Pillow.render_pillow_dashboard(
        rail_nb=rail_client.get_departures(
            4, config.stations.northbound_from, config.stations.northbound_to
        ),
        rail_sb=rail_client.get_departures(
            4, config.stations.southbound_from, config.stations.southbound_to
        ),
        temperature_data=get_weather(),
    )

    log.info("Displaying image and saving preview.png")
    pil_image.save("preview.png")
    # send_to_display(pil_image)
    send_to_server(pil_image)


@app.post("/update")
async def update_dashboard(background_tasks: BackgroundTasks):
    """
    Endpoint to manually trigger the dashboard update
    """
    background_tasks.add_task(run_dashboard_update)
    return {"message": "Dashboard update scheduled"}


@app.post("/config")
async def update_config(
    new_config: UpdateConfig, api_config: APIConfig = Depends(get_apiconfig)
):
    """
    Endpoint to update the dashboard update frequency
    """
    api_config.update_interval = datetime.timedelta(minutes=new_config.interval_minutes)
    return {"message": "Dashboard update frequency updated"}


def main():
    """Program Entrypoint"""
    try:
        run_dashboard_update()  # Run the dashboard update initially

        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

    except IOError as exception:
        log.info(exception)

    except KeyboardInterrupt:
        log.info("ctrl + c:")
        epdconfig.RaspberryPi().module_exit()
        sys.exit()


if __name__ == "__main__":
    main()
