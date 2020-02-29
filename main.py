#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
from pathlib import Path
from datetime import datetime
import configparser
import logging

import textwrap
import requests

from zeep import Client
from zeep import xsd
from zeep.plugins import HistoryPlugin

from waveshare_epd import epd7in5_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

config = configparser.ConfigParser()
config.read('configuration.ini')
stations = {
    'North': {
        'from': config['stations']['northbound_from'],
        'to': config['stations']['northbound_to']
    },
    'South': {
        'from': config['stations']['southbound_from'],
        'to': config['stations']['sountbound_to']
    }
}

LDB_TOKEN = config['tokens']['national_rail']
WSDL = 'http://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2017-10-01'
history = HistoryPlugin()
client = Client(wsdl=WSDL, plugins=[history])
header = xsd.Element(
    '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}AccessToken',
    xsd.ComplexType([
        xsd.Element(
            '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}TokenValue',
            xsd.String()),
    ])
)
header_value = header(TokenValue=LDB_TOKEN)
def getDepartures(numRows,atStation, toStation):
    response = client.service.GetDepartureBoard(numRows=numRows, crs=atStation, filterCrs=toStation, _soapheaders=[header_value])
    return response

fontdir = os.path.join(Path(__file__).parent, 'fonts')
logging.basicConfig(level=logging.DEBUG)
print(os.path.join(fontdir, 'Overpass/Overpass-ExtraLight.ttf'))
font_time = ImageFont.truetype(os.path.join(fontdir, 'Overpass/Overpass-ExtraLight.ttf'), 95)
font_direction = ImageFont.truetype(os.path.join(fontdir, 'Overpass/Overpass-Light.ttf'), 23)
font_traininfo = ImageFont.truetype(os.path.join(fontdir, 'Overpass/Overpass-Light.ttf'), 15)
font_dayofweek = ImageFont.truetype(os.path.join(fontdir, 'Overpass/Overpass-SemiBold.ttf'), 65)
font_date = ImageFont.truetype(os.path.join(fontdir, 'Overpass/Overpass-ExtraLight.ttf'), 65)
font_bigtemp = ImageFont.truetype(os.path.join(fontdir, 'Overpass/Overpass-ExtraLight.ttf'), 75)
font_smalltemp = ImageFont.truetype(os.path.join(fontdir, 'Overpass/Overpass-ExtraLight.ttf'), 27)

def drawDeparturesIssue(draw, y, departures):
    # Either return blank or display engineering message
    try:
        message = departures.nrccMessages.message[0]._value_1
    except:
        return 0
    # The message is long with a link to their website, so split it at the .
    message = message.split('.', 1)[0]
    lines = textwrap.wrap(message, width=50)
    print(message)
    #draw.text((train_columns[0], y), message,  font = font_traininfo, fill = 0)
    y_text = y
    for line in lines:
        width, height = draw.textsize(line, font = font_traininfo)
        draw.text(((train_columns[0]), y_text), line, font=font_traininfo)
        y_text += height  

train_columns = [0,0,0,0]
train_columns[0] = 60
train_columns[1] = train_columns[0] + 73
train_columns[2] = train_columns[1] + 167
train_columns[3] = train_columns[2] + 103
train_line_offset = 19
def drawDepartures(draw, y, now, departures):
    try:
        services = departures.trainServices.service
    except:
      drawDeparturesIssue(draw, y,  departures)
      return 0

    for service in services:
        now_hours = datetime.strptime(now.strftime("%H:%M"),'%H:%M') 
        arrival_time = datetime.strptime( service.std, '%H:%M')
        time_until = arrival_time - now_hours
        time_until_minutes = int(time_until.total_seconds() / 60)
        if time_until_minutes > 60:
            hours, minutes = divmod(time_until_minutes, 60)
            time_until_text = f'{hours} HR {minutes} MINS'
        else: 
            time_until_text = f'{time_until_minutes} MINS'        
        print(time_until_minutes)
        draw.text((train_columns[0], y), service.std,  font = font_traininfo, fill = 0)
        draw.text((train_columns[1], y), service.destination.location[0].locationName.upper(),  font = font_traininfo, fill = 0)
        draw.text((train_columns[2], y), service.etd.upper(),  font = font_traininfo, fill = 0)
        draw.text((train_columns[3], y), time_until_text,  font = font_traininfo, fill = 0)
        y += train_line_offset



def roundThenString(number):
    return str(int(round(number)))
def getWeather():
    """Get Weather from Open Weather Map API

    Params:
    id -- the id of the town from http://bulk.openweathermap.org/sample/city.list.json.gz
    units -- metric, imperial or kelvin
    APPID -- API Key (Register Here: https://openweathermap.org/api)
    """
    endpoint = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "id": config['weather']['townID'],
        "units": "metric",
        "APPID": config['tokens']['open_weather_map']
    }
    resp = requests.get(url=endpoint, params=params)
    data = resp.json()
    print(data)
    temp = {
        "Average": roundThenString(data['main']['temp']),
        "High": roundThenString(data['main']['temp_max']),
        "Low": roundThenString(data['main']['temp_min']),
        "Weather": data['weather'][0]['main']
    }
    return temp

def loadSvgAsPIL(path):
    return renderPM.drawToPIL(svg2rlg(path))

def getWeatherIcon(weather):
    if weather == "Thunderstorm":
        return loadSvgAsPIL("./weather_icons/057-storm-7.svg")
    if weather == "Drizzle":
        return loadSvgAsPIL("./weather_icons/099-rain-4.svg")
    if weather == "Rain":
        return loadSvgAsPIL("./weather_icons/067-storm-6.svg")
    if weather == "Snow":
        return loadSvgAsPIL("./weather_icons/047-snow-4.svg")                
    if weather == "Atmosphere":
        return loadSvgAsPIL("./weather_icons/091-sunrise.svg")
    if weather == "Clear":
        return loadSvgAsPIL("./weather_icons/013-sun-8.svg")
    if weather == "Clouds":
        return loadSvgAsPIL("./weather_icons/051-cloud-3.svg")                

def drawWeather(image, weather):
    icon = getWeatherIcon(weather)
    icon.thumbnail((160,165), Image.ANTIALIAS)
    image.paste(icon, (550,170))



def smallTempPosition(text, tempEndPosition):
    print(tempEndPosition)
    text_length = draw.textsize(text, font = font_smalltemp)[0]
    return tempEndPosition - text_length - 8
    

def drawTemp(image, draw, tempEndPosition):
    temp = getWeather()
    hightext = f'{temp["High"]}°C'
    lowtext = f'{temp["Low"]}°C'
    draw.text((smallTempPosition(hightext, tempEndPosition), 365),  hightext, font = font_smalltemp, fill = 0)
    draw.text((smallTempPosition(lowtext, tempEndPosition), 400),  lowtext, font = font_smalltemp, fill = 0)
    draw.text((560,352), f'{temp["Average"]}°C', font = font_bigtemp, fill = 0)
    drawWeather(image, temp['Weather'])
    
try:
    logging.info("epd7in5_V2 Demo")

    epd = epd7in5_V2.EPD()
    logging.info("init and Clear")
    epd.init()
    #epd.Clear()

    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    now = datetime.now()
    dt_string = now.strftime("%H:%M")
    dt_dayofweek = now.strftime("%a").upper()
    dt_date = now.strftime("%d")
    dt_month = now.strftime("%b").upper()
    draw.text((40, 15), dt_string, font = font_time, fill = 0)
    date_y = 25
    
    length_dayofweek = draw.textsize(dt_dayofweek, font = font_dayofweek)[0]
    length_date = draw.textsize(dt_date, font = font_date)[0]
    length_month = draw.textsize(dt_month, font = font_date)[0]
    dayofweek_start_position = 428
    date_start_position = dayofweek_start_position+length_dayofweek+10
    month_start_position = date_start_position+length_date+10
    date_x_positions = [dayofweek_start_position, date_start_position, month_start_position]
    draw.text((date_x_positions[0], date_y), dt_dayofweek, font = font_dayofweek, fill = 0)
    draw.text((date_x_positions[1], date_y), dt_date, font = font_date, fill = 0)
    draw.text((date_x_positions[2], date_y), dt_month, font = font_date, fill = 0)
    draw.text((60, 168), 'NORTHBOUND', font = font_direction, fill = 0)
    drawDepartures(draw, 210, now, getDepartures(4, stations['North']['from'], stations['North']['to']))
    draw.text((60, 312), 'SOUTHBOUND', font = font_direction, fill = 0)
    drawDepartures(draw, 356, now, getDepartures(4, stations['South']['from'], stations['South']['to']))
    drawTemp(Himage, draw, month_start_position+length_month)
    
    Himage.save("preview.png")


    epd.display(epd.getbuffer(Himage))

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5.epdconfig.module_exit()
    exit()

