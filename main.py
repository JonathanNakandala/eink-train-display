"""
Home Dashboard for a WaveShare 7.5 e-ink display with Raspberry PI
"""
import sys

import structlog

from sources import NationalRail, Weather
from render import Pillow
from waveshare_epd import epd7in5_V2, epdconfig

from config import load_config

log = structlog.get_logger()

config = load_config()


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


def send_to_display(pil_image):
    """
    Send Data to Display
    """
    epd = epd7in5_V2.EPD()
    # epd.Clear()
    log.info("Initialising the display...")
    epd.init()
    epd.display(epd.getbuffer(pil_image))
    log.info("Sending Display to Sleep")
    epd.sleep()


def main():
    """Program Entrypoint"""
    try:
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
        send_to_display(pil_image)
    except IOError as exception:
        log.info(exception)

    except KeyboardInterrupt:
        log.info("ctrl + c:")
        epdconfig.RaspberryPi().module_exit()
        sys.exit()


main()
