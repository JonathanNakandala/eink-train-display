"""
Home Dashboard for a WaveShare 7.5 e-ink display with Raspberry PI
"""
import configparser
import logging
import os
import sys
import textwrap
from datetime import datetime
from pathlib import Path

import structlog
import requests
from PIL import Image, ImageDraw, ImageFont
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

from sources import NationalRail
from waveshare_epd import epd7in5_V2, epdconfig

log = structlog.get_logger()

config = configparser.ConfigParser()
config.read(os.path.join(Path(__file__).parent, "configuration.ini"))
stations = {
    "North": {
        "from": config["stations"]["northbound_from"],
        "to": config["stations"]["northbound_to"],
    },
    "South": {
        "from": config["stations"]["southbound_from"],
        "to": config["stations"]["sountbound_to"],
    },
}


fontdir = os.path.join(Path(__file__).parent, "fonts")
# logging.basicConfig(level=logging.DEBUG)
print(os.path.join(fontdir, "Overpass/Overpass-ExtraLight.ttf"))
font_time = ImageFont.truetype(
    os.path.join(fontdir, "Overpass/Overpass-ExtraLight.ttf"), 95
)
font_direction = ImageFont.truetype(
    os.path.join(fontdir, "Overpass/Overpass-Light.ttf"), 23
)
font_traininfo = ImageFont.truetype(
    os.path.join(fontdir, "Overpass/Overpass-Light.ttf"), 15
)
font_dayofweek = ImageFont.truetype(
    os.path.join(fontdir, "Overpass/Overpass-SemiBold.ttf"), 65
)
font_date = ImageFont.truetype(
    os.path.join(fontdir, "Overpass/Overpass-ExtraLight.ttf"), 65
)
font_bigtemp = ImageFont.truetype(
    os.path.join(fontdir, "Overpass/Overpass-ExtraLight.ttf"), 75
)
font_smalltemp = ImageFont.truetype(
    os.path.join(fontdir, "Overpass/Overpass-ExtraLight.ttf"), 27
)


def draw_departure_issues(draw, y_position, departures):
    """
    Either return blank or display engineering message when no results

    Args:
        draw: _description_
        y: _description_
        departures: _description_

    Returns:
        _description_
    """
    #
    try:
        message = departures.nrccMessages.message[0]._value_1  # pylint: disable=W0212
    except KeyError:
        return 0
    # The message is long with a link to their website, so split it at the .
    message = message.split(".", 1)[0]
    lines = textwrap.wrap(message, width=50)
    print(message)
    # draw.text((train_columns[0], y), message,  font = font_traininfo, fill = 0)
    y_text = y_position
    for line in lines:
        _, height = draw.textsize(line, font=font_traininfo)
        draw.text(((train_columns[0]), y_text), line, font=font_traininfo)
        y_text += height


train_columns = [0, 0, 0, 0]
train_columns[0] = 60
train_columns[1] = train_columns[0] + 73
train_columns[2] = train_columns[1] + 167
train_columns[3] = train_columns[2] + 103
TRAIN_LINE_OFFSET = 19


def draw_departures(draw, y_position, now, departures):
    """
    Draw the Train Departures Information

    Args:
        draw: _description_
        y: _description_
        now: _description_
        departures: _description_

    Returns:
        _description_
    """
    try:
        services = departures.trainServices.service
    except KeyError:
        draw_departure_issues(draw, y_position, departures)
        return 0

    for service in services:
        now_hours = datetime.strptime(now.strftime("%H:%M"), "%H:%M")
        arrival_time = datetime.strptime(service.std, "%H:%M")
        time_until = arrival_time - now_hours
        time_until_minutes = int(time_until.total_seconds() / 60)
        if time_until_minutes > 60:
            hours, minutes = divmod(time_until_minutes, 60)
            time_until_text = f"{hours} HR {minutes} MINS"
        else:
            time_until_text = f"{time_until_minutes} MINS"
        print(time_until_minutes)
        draw.text(
            (train_columns[0], y_position), service.std, font=font_traininfo, fill=0
        )
        draw.text(
            (train_columns[1], y_position),
            service.destination.location[0].locationName.upper(),
            font=font_traininfo,
            fill=0,
        )
        draw.text(
            (train_columns[2], y_position),
            service.etd.upper(),
            font=font_traininfo,
            fill=0,
        )
        draw.text(
            (train_columns[3], y_position), time_until_text, font=font_traininfo, fill=0
        )
        y_position += TRAIN_LINE_OFFSET


def round_number_to_string(number: int) -> str:
    """Round an int and convert to string"""
    return str(int(round(number)))


def get_weather():
    """
    Get Weather from Open Weather Map API

    Args:
    id: the id of the town from http://bulk.openweathermap.org/sample/city.list.json.gz
    unit: metric, imperial or kelvin
    app_id: API Key (Register Here: https://openweathermap.org/api)

    Returns:
    Temperature Data
    """
    endpoint = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "id": config["weather"]["townID"],
        "units": "metric",
        "APPID": config["tokens"]["open_weather_map"],
    }
    resp = requests.get(url=endpoint, params=params, timeout=10)
    data = resp.json()
    print(data)
    temp = {
        "Average": round_number_to_string(data["main"]["temp"]),
        "High": round_number_to_string(data["main"]["temp_max"]),
        "Low": round_number_to_string(data["main"]["temp_min"]),
        "Weather": data["weather"][0]["main"],
    }
    return temp


def load_svg_to_pil(path: str):
    """
    Load svg as a Pillow Image

    Args:
        path: path to svg

    Returns:
        Image
    """
    return renderPM.drawToPIL(svg2rlg(path))


def get_weather_icon(weather):
    """
    Returns the Pillow Image for the Weather Icon

    Args:
        weather: Weather Types

    Returns:
        Image
    """

    if weather == "Thunderstorm":
        return load_svg_to_pil("./weather_icons/057-storm-7.svg")
    if weather == "Drizzle":
        return load_svg_to_pil("./weather_icons/099-rain-4.svg")
    if weather == "Rain":
        return load_svg_to_pil("./weather_icons/067-storm-6.svg")
    if weather == "Snow":
        return load_svg_to_pil("./weather_icons/047-snow-4.svg")
    if weather == "Atmosphere":
        return load_svg_to_pil("./weather_icons/091-sunrise.svg")
    if weather == "Clear":
        return load_svg_to_pil("./weather_icons/013-sun-8.svg")
    if weather == "Clouds":
        return load_svg_to_pil("./weather_icons/051-cloud-3.svg")


def draw_weather(image, weather):
    """
    Draws the Weather Icon

    Args:
        image: the image canvas to draw onto to
        weather: Weather description
    """
    icon = get_weather_icon(weather)
    icon.thumbnail((160, 165), Image.ANTIALIAS)
    image.paste(icon, (550, 170))


def small_temp_position(draw, text, temp_end_position):
    """
    Determines the position for the small temperature (min/max)
    Args:
        draw: _description_
        text: _description_
        temp_end_position: _description_

    Returns:
        Position
    """
    print(temp_end_position)
    text_length = draw.textsize(text, font=font_smalltemp)[0]
    return temp_end_position - text_length - 8


def draw_temp(image, draw: ImageDraw, temp_end_position):
    """
    Draw the temperature, min/max and icon

    Args:
        image: _description_
        draw: _description_
        temp_end_position: _description_
    """
    temp = get_weather()
    hightext = f'{temp["High"]}°C'
    lowtext = f'{temp["Low"]}°C'
    draw.text(
        (small_temp_position(draw, hightext, temp_end_position), 365),
        hightext,
        font=font_smalltemp,
        fill=0,
    )
    draw.text(
        (small_temp_position(draw, lowtext, temp_end_position), 400),
        lowtext,
        font=font_smalltemp,
        fill=0,
    )
    draw.text((560, 352), f'{temp["Average"]}°C', font=font_bigtemp, fill=0)
    draw_weather(image, temp["Weather"])


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
        # Create blank monochrome image to draw onto
        pil_image = Image.new("1", (800, 480), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(pil_image)
        log.info("Drawing the time")
        now = datetime.now()
        time_string = now.strftime("%H:%M")
        draw.text((40, 15), time_string, font=font_time, fill=0)

        log.info("Drawing the date")
        dt_dayofweek = now.strftime("%a").upper()
        dt_date = now.strftime("%d")
        dt_month = now.strftime("%b").upper()
        date_y = 25
        length_dayofweek = draw.textsize(dt_dayofweek, font=font_dayofweek)[0]
        length_date = draw.textsize(dt_date, font=font_date)[0]
        length_month = draw.textsize(dt_month, font=font_date)[0]
        dayofweek_start_position = 428
        date_start_position = dayofweek_start_position + length_dayofweek + 10
        month_start_position = date_start_position + length_date + 10
        date_x_positions = [
            dayofweek_start_position,
            date_start_position,
            month_start_position,
        ]
        draw.text(
            (date_x_positions[0], date_y), dt_dayofweek, font=font_dayofweek, fill=0
        )
        draw.text((date_x_positions[1], date_y), dt_date, font=font_date, fill=0)
        draw.text((date_x_positions[2], date_y), dt_month, font=font_date, fill=0)

        log.info("Drawing the Train Arrivals")
        rail_client = NationalRail.NationalRail(config["tokens"]["national_rail"])
        draw.text((60, 168), "NORTHBOUND", font=font_direction, fill=0)
        draw_departures(
            draw,
            210,
            now,
            rail_client.get_departures(
                4, stations["North"]["from"], stations["North"]["to"]
            ),
        )
        draw.text((60, 312), "SOUTHBOUND", font=font_direction, fill=0)
        draw_departures(
            draw,
            356,
            now,
            rail_client.get_departures(
                4, stations["South"]["from"], stations["South"]["to"]
            ),
        )
        draw_temp(pil_image, draw, month_start_position + length_month)

        log.info("Displaying image and saving preview.png")
        pil_image.save("preview.png")

    except IOError as exception:
        log.info(exception)

    except KeyboardInterrupt:
        log.info("ctrl + c:")
        epdconfig.RaspberryPi().module_exit()
        sys.exit()


main()
