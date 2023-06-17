"""
Render the screen output using a Pillow Image
"""
import textwrap
from datetime import datetime, timedelta
from PIL import ImageDraw

import structlog
from . import fonts

log = structlog.get_logger()
train_columns = [0, 0, 0, 0]
train_columns[0] = 60
train_columns[1] = train_columns[0] + 73
train_columns[2] = train_columns[1] + 167
train_columns[3] = train_columns[2] + 103
TRAIN_LINE_OFFSET = 19


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
    if departures.nrccMessages is not None:
        message = departures.nrccMessages.message[0]._value_1  # pylint: disable=W0212
        # The message is long with a link to their website, so split it at the .
        message = message.split(".", 1)[0]
    else:
        message = "No scheduled trains"
    lines = textwrap.wrap(message, width=50)
    # draw.text((train_columns[0], y), message,  font = font_traininfo, fill = 0)
    y_text = y_position
    for line in lines:
        _, height = draw.textsize(line, font=fonts.font_traininfo)
        draw.text(((train_columns[0]), y_text), line, font=fonts.font_traininfo)
        y_text += height


def get_time_until_next_train(time_now: datetime, service):
    """
    Generate time until next train
    """
    now_hours = datetime.strptime(time_now.strftime("%H:%M"), "%H:%M")
    arrival_time = datetime.strptime(service.std, "%H:%M")

    # Check if arrival_time is earlier than now_hours
    if arrival_time < now_hours:
        # if so, add one day to the arrival_time
        arrival_time += timedelta(days=1)

    time_until = arrival_time - now_hours
    time_until_minutes = int(time_until.total_seconds() / 60)

    if time_until_minutes > 60:
        hours, minutes = divmod(time_until_minutes, 60)
        time_until_text = f"{hours} HR {minutes} MINS"
    else:
        time_until_text = f"{time_until_minutes} MINS"

    return time_until_text


def draw_departures(draw: ImageDraw, y_position, time_now: datetime, departures):
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
    except (KeyError, AttributeError):
        log.error("Failed to read trains", data=departures)
        draw_departure_issues(draw, y_position, departures)
        return

    for service in services:
        time_until_text = get_time_until_next_train(time_now, service)
        draw.text(
            (train_columns[0], y_position),
            service.std,
            font=fonts.font_traininfo,
            fill=0,
        )
        draw.text(
            (train_columns[1], y_position),
            service.destination.location[0].locationName.upper()[0:17],
            font=fonts.font_traininfo,
            fill=0,
        )
        draw.text(
            (train_columns[2], y_position),
            service.etd.upper(),
            font=fonts.font_traininfo,
            fill=0,
        )
        draw.text(
            (train_columns[3], y_position),
            time_until_text,
            font=fonts.font_traininfo,
            fill=0,
        )
        y_position += TRAIN_LINE_OFFSET
