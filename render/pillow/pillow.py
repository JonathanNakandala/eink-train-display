"""
Render with Pillow
"""
from datetime import datetime

import structlog
from PIL import Image, ImageDraw

from sources.national_rail.models import DeparturesResponse
from . import fonts, departures, climate

log = structlog.get_logger()


def draw_time(draw: ImageDraw, time: datetime):
    """
    Draw time
    """
    log.info("Drawing the time")
    time_string = time.strftime("%H:%M")
    draw.text((40, 15), time_string, font=fonts.font_time, fill=0)


def draw_date(draw: ImageDraw, time: datetime) -> tuple:
    """
    Draw the date
    """
    log.info("Drawing the date")
    dt_dayofweek = time.strftime("%a").upper()
    dt_date = time.strftime("%d")
    dt_month = time.strftime("%b").upper()
    date_y = 25
    length_dayofweek = draw.textsize(dt_dayofweek, font=fonts.font_dayofweek)[0]
    length_date = draw.textsize(dt_date, font=fonts.font_date)[0]
    length_month = draw.textsize(dt_month, font=fonts.font_date)[0]
    dayofweek_start_position = 428
    date_start_position = dayofweek_start_position + length_dayofweek + 10
    month_start_position = date_start_position + length_date + 10
    date_x_positions = [
        dayofweek_start_position,
        date_start_position,
        month_start_position,
    ]
    draw.text(
        (date_x_positions[0], date_y), dt_dayofweek, font=fonts.font_dayofweek, fill=0
    )
    draw.text((date_x_positions[1], date_y), dt_date, font=fonts.font_date, fill=0)
    draw.text((date_x_positions[2], date_y), dt_month, font=fonts.font_date, fill=0)
    return length_month, month_start_position


def render_pillow_dashboard(
    rail_nb: DeparturesResponse, rail_sb: DeparturesResponse, temperature_data: dict
) -> Image:
    """
    Render the Pillow Dashboard
    """
    # Create blank monochrome image to draw onto
    pil_image = Image.new("1", (800, 480), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(pil_image)

    time_now = datetime.now()
    log.info("Current Time", time=time_now.isoformat())
    draw_time(draw, time_now)
    length_month, month_start_position = draw_date(draw, time_now)
    log.info("Drawing the Train Arrivals")
    draw.text((60, 168), "NORTHBOUND", font=fonts.font_direction, fill=0)
    departures.draw_departures(
        draw,
        210,
        time_now,
        rail_nb,
    )
    draw.text((60, 312), "SOUTHBOUND", font=fonts.font_direction, fill=0)
    departures.draw_departures(
        draw,
        356,
        time_now,
        rail_sb,
    )
    climate.draw_temp(
        temperature_data, pil_image, draw, month_start_position + length_month
    )
    return pil_image
