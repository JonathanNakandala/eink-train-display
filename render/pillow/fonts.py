"""
Fonts used by pillow
"""
from pathlib import Path

import structlog
from PIL import ImageFont

log = structlog.get_logger()

fontdir = Path(__file__).parent.parent.parent / "fonts"
log.info("Font Directory", dir=fontdir)
font_time = ImageFont.truetype(str(fontdir / "Overpass/Overpass-ExtraLight.ttf"), 95)
font_direction = ImageFont.truetype(str(fontdir / "Overpass/Overpass-Light.ttf"), 23)
font_traininfo = ImageFont.truetype(str(fontdir / "Overpass/Overpass-Light.ttf"), 15)
font_dayofweek = ImageFont.truetype(str(fontdir / "Overpass/Overpass-SemiBold.ttf"), 65)
font_date = ImageFont.truetype(str(fontdir / "Overpass/Overpass-ExtraLight.ttf"), 65)
font_bigtemp = ImageFont.truetype(str(fontdir / "Overpass/Overpass-ExtraLight.ttf"), 75)
font_smalltemp = ImageFont.truetype(
    str(fontdir / "Overpass/Overpass-ExtraLight.ttf"), 27
)
