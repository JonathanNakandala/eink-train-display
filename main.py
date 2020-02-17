#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
from pathlib import Path
from datetime import datetime
import configparser
config = configparser.ConfigParser()
config.read('configuration.ini')

from zeep import Client
from zeep import xsd
from zeep.plugins import HistoryPlugin

import logging
from waveshare_epd import epd7in5_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

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

train_columns = [60, 133, 295, 403]
train_line_offset = 19
def drawDepartures(draw, y, now, departures):
    services = departures.trainServices.service
    for service in services:
        now_hours = datetime.strptime(now.strftime("%H:%M"),'%H:%M') 
        arrival_time = datetime.strptime( service.std, '%H:%M')
        time_until = arrival_time - now_hours
        time_until_minutes = int(time_until.total_seconds() / 60)
        print(time_until_minutes)
        draw.text((train_columns[0], y), service.std,  font = font_traininfo, fill = 0)
        draw.text((train_columns[1], y), service.destination.location[0].locationName.upper(),  font = font_traininfo, fill = 0)
        draw.text((train_columns[2], y), service.etd.upper(),  font = font_traininfo, fill = 0)
        draw.text((train_columns[3], y), f'{time_until_minutes} MINS',  font = font_traininfo, fill = 0)
        y += train_line_offset

def getTemp():
    return 14

def drawTemp(draw):
    draw.text((540,352), "14°C", font = font_bigtemp, fill = 0)
    #draw.text((360, 540), 'NORTHBOUND', font = font_direction, fill = 0)
    print("Hello")

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
    draw.text((428, 25), dt_dayofweek, font = font_dayofweek, fill = 0)
    draw.text((565, 25), dt_date, font = font_date, fill = 0)
    draw.text((635, 25), dt_month, font = font_date, fill = 0)
    draw.text((60, 168), 'NORTHBOUND', font = font_direction, fill = 0)
    drawDepartures(draw, 210, now, getDepartures(4, 'HRN', 'WIH'))
    draw.text((60, 312), 'SOUTHBOUND', font = font_direction, fill = 0)
    drawDepartures(draw, 356, now, getDepartures(4, 'HRN', 'FPK'))
    drawTemp(draw)
    #draw.text((360, 540), 'NORTHBOUND', font = font_direction, fill = 0)
    
    Himage.save("preview.png")
    Himage.resize((epd.width*4, epd.height*4), Image.ANTIALIAS)
    Himage.resize((epd.width, epd.height), Image.ANTIALIAS)
    Himage.save("preview2.png")



    epd.display(epd.getbuffer(Himage))

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5.epdconfig.module_exit()
    exit()

