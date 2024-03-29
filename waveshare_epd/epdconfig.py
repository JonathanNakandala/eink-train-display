"""
Waveshare's EPD config file
"""
# /*****************************************************************************
# * | File        :	  epdconfig.py
# * | Author      :   Waveshare team
# * | Function    :   Hardware underlying interface
# * | Info        :
# *----------------
# * | This version:   V1.2-jon
# * | Date        :   2022-10-29
# * | Info        :
# ******************************************************************************
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import sys
import time
import structlog
import spidev


log = structlog.getLogger()


class RaspberryPi:
    """ "
    Class for using Waveshare 7.5" B/W with Raspberry PI
    """

    # Pin definition
    RST_PIN = 17
    DC_PIN = 25
    CS_PIN = 8
    BUSY_PIN = 24
    PWR_PIN = 18

    def __init__(self):
        from RPi import GPIO  # pylint: disable=C0415

        GPIO.output: callable
        GPIO.input: callable
        GPIO.setmode: callable
        GPIO.setup: callable
        GPIO.setwarnings: callable
        GPIO.cleanup: callable
        GPIO.BCM: callable
        GPIO.IN: callable
        GPIO.OUT: callable
        self.GPIO = GPIO  # pylint: disable=C0103
        self.SPI = spidev.SpiDev()  # pylint: disable=C0103

    def digital_write(self, pin: int, value: int):
        """
        Write value to GPIO Pin
        """
        self.GPIO.output(pin, value)

    def digital_read(self, pin: int) -> int:
        """
        Read Value from GPIO pin
        """
        return self.GPIO.input(pin)

    def delay_ms(self, delaytime: int):
        """
        Sleep for set amount of milliseconds
        """
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data: bytes):
        """
        Write a list of values to SPI device
        """
        self.SPI.writebytes(data)

    def spi_writebyte2(self, data: bytearray):
        """
        Writes data to SPI
        Accepts a bytearray directly
        """
        self.SPI.writebytes2(data)

    def module_init(self):
        """
        This function sets up the GPIO, turns on the power,
        and opens an SPI interface for communication with the display.
        """
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setwarnings(False)
        self.GPIO.setup(self.RST_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.DC_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.CS_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.PWR_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.BUSY_PIN, self.GPIO.IN)

        self.GPIO.output(self.PWR_PIN, 1)

        # SPI device, bus = 0, device = 0
        self.SPI.open(0, 0)
        self.SPI.max_speed_hz = 4000000
        self.SPI.mode = 0b00
        return 0

    def module_exit(self):
        """
        Shut down the SPI interface, turns off the power to the display, and cleans up the GPIO.
        Note: After calling this function, display needs to be initialized again.
        """
        log.debug("Ending SPI connection.")
        self.SPI.close()

        log.debug(
            "Shutting down power to the display. Entering zero power consumption mode..."
        )
        self.GPIO.output(self.RST_PIN, 0)
        self.GPIO.output(self.DC_PIN, 0)
        self.GPIO.output(self.PWR_PIN, 0)

        log.debug("Cleaning up GPIO.")
        self.GPIO.cleanup(
            [self.RST_PIN, self.DC_PIN, self.CS_PIN, self.BUSY_PIN, self.PWR_PIN]
        )
        log.info("Display Powered Down")


class Dummy:
    """
    Does Nothing
    """

    RST_PIN = 17
    DC_PIN = 25
    CS_PIN = 8
    BUSY_PIN = 24

    def digital_write(self, pin, value):
        """Dummy"""

    def digital_read(self, pin):
        """Dummy"""

    def delay_ms(self, delaytime):
        """Dummy"""

    def spi_writebyte(self, data):
        """Dummy"""

    def spi_writebyte2(self, data):
        """Dummy"""

    def module_init(self):
        """Dummy"""
        return 0

    def module_exit(self):
        """Dummy"""
        log.debug("spi end")


if os.path.exists("/sys/bus/platform/drivers/gpiomem-bcm2835"):
    implementation = RaspberryPi()
else:
    implementation = Dummy()

for func in [x for x in dir(implementation) if not x.startswith("_")]:
    setattr(sys.modules[__name__], func, getattr(implementation, func))
