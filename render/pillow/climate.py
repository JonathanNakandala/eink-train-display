"""
Render the weather data
"""
from pathlib import Path
from PIL import ImageDraw, Image
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import structlog
from . import fonts

log = structlog.get_logger()


def get_weather_icon(weather):
    """
    Returns the Pillow Image for the Weather Icon

    Args:
        weather: Weather Types

    Returns:
        Image
    """

    base_path = Path(__file__).parent.parent.parent / "weather_icons"
    match weather:
        case "Thunderstorm":
            svg_file = base_path / "057-storm-7.svg"
        case "Drizzle":
            svg_file = base_path / "099-rain-4.svg"
        case "Rain":
            svg_file = base_path / "067-storm-6.svg"
        case "Snow":
            svg_file = base_path / "047-snow-4.svg"
        case "Atmosphere":
            svg_file = base_path / "091-sunrise.svg"
        case "Clear":
            svg_file = base_path / "013-sun-8.svg"
        case "Clouds":
            svg_file = base_path / "051-cloud-3.svg"
        case _:
            raise ValueError(f"Unknown weather type: {weather}")
    log.info("SVG Path for Weather", path=svg_file)
    return renderPM.drawToPIL(svg2rlg(svg_file))


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
    text_length = draw.textsize(text, font=fonts.font_smalltemp)[0]
    return temp_end_position - text_length + 28


def draw_temp(temp, image, draw: ImageDraw, temp_end_position):
    """
    Draw the temperature, min/max and icon

    Args:
        image: _description_
        draw: _description_
        temp_end_position: _description_
    """
    hightext = f'{temp["High"]}°C'
    lowtext = f'{temp["Low"]}°C'
    offset = -10
    draw.text(
        (small_temp_position(draw, hightext, temp_end_position), 365 + offset),
        hightext,
        font=fonts.font_smalltemp,
        fill=0,
    )
    draw.text(
        (small_temp_position(draw, lowtext, temp_end_position), 400 + offset),
        lowtext,
        font=fonts.font_smalltemp,
        fill=0,
    )
    draw.text((560, 352), f'{temp["Average"]}°C', font=fonts.font_bigtemp, fill=0)
    draw_weather(image, temp["Weather"])
