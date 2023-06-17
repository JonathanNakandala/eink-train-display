"""
Modified epd7in5 from waveshare
"""
# *****************************************************************************
# * | File        :	  epd7in5.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V4.0-jon
# * | Date        :   2019-06-20
# # | Info        :   python demo
# -----------------------------------------------------------------------------
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
import structlog
from PIL import Image


log = structlog.getLogger()
# Display resolution
EPD_WIDTH = 800
EPD_HEIGHT = 480


class EPD:
    """
    E-ink paper display handling class
    Supports running as dummy class when not on a raspberry pi
    """

    def __init__(self):
        if os.path.exists("/sys/bus/platform/drivers/gpiomem-bcm2835"):
            from .epdconfig import RaspberryPi  # pylint: disable=C0415

            self.epdconfig = RaspberryPi()
        else:
            from .epdconfig import Dummy  # pylint: disable=C0415

            self.epdconfig = Dummy()

        self.reset_pin = self.epdconfig.RST_PIN
        self.dc_pin = self.epdconfig.DC_PIN
        self.busy_pin = self.epdconfig.BUSY_PIN
        self.cs_pin = self.epdconfig.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    # fmt: off
    Voltage_Frame_7IN5_V2 = [
	0x6, 0x3F, 0x3F, 0x11, 0x24, 0x7, 0x17,
    ]

    LUT_VCOM_7IN5_V2 = [
        0x0,	0xF,	0xF,	0x0,	0x0,	0x1,
        0x0,	0xF,	0x1,	0xF,	0x1,	0x2,
        0x0,	0xF,	0xF,	0x0,	0x0,	0x1,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
    ]

    LUT_WW_7IN5_V2 = [
        0x10,	0xF,	0xF,	0x0,	0x0,	0x1,
        0x84,	0xF,	0x1,	0xF,	0x1,	0x2,
        0x20,	0xF,	0xF,	0x0,	0x0,	0x1,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
    ]

    LUT_BW_7IN5_V2 = [
        0x10,	0xF,	0xF,	0x0,	0x0,	0x1,
        0x84,	0xF,	0x1,	0xF,	0x1,	0x2,
        0x20,	0xF,	0xF,	0x0,	0x0,	0x1,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
    ]

    LUT_WB_7IN5_V2 = [
        0x80,	0xF,	0xF,	0x0,	0x0,	0x1,
        0x84,	0xF,	0x1,	0xF,	0x1,	0x2,
        0x40,	0xF,	0xF,	0x0,	0x0,	0x1,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
    ]

    LUT_BB_7IN5_V2 = [
        0x80,	0xF,	0xF,	0x0,	0x0,	0x1,
        0x84,	0xF,	0x1,	0xF,	0x1,	0x2,
        0x40,	0xF,	0xF,	0x0,	0x0,	0x1,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
        0x0,	0x0,	0x0,	0x0,	0x0,	0x0,
    ]

    # fmt: on
    def reset(self):
        """
        Resets the e-paper display by cycling the reset pin.
            - Sends HIGH to the pin
            - Pauses for 20ms on HIGH
            - Sends LOW to the pin
            - Pauses for 2ms on LOW
        """
        self.epdconfig.digital_write(self.reset_pin, 1)
        self.epdconfig.delay_ms(20)
        self.epdconfig.digital_write(self.reset_pin, 0)
        self.epdconfig.delay_ms(2)
        self.epdconfig.digital_write(self.reset_pin, 1)
        self.epdconfig.delay_ms(20)

    def send_command(self, command):
        """
        Sends a command to the e-paper display.
        """
        self.epdconfig.digital_write(self.dc_pin, 0)
        self.epdconfig.digital_write(self.cs_pin, 0)
        self.epdconfig.spi_writebyte([command])
        self.epdconfig.digital_write(self.cs_pin, 1)

    def send_data(self, data: int):
        """
        Sends data to the e-paper display.
        """
        self.epdconfig.digital_write(self.dc_pin, 1)
        self.epdconfig.digital_write(self.cs_pin, 0)
        self.epdconfig.spi_writebyte([data])
        self.epdconfig.digital_write(self.cs_pin, 1)

    def send_data2(self, data: bytearray | list[int]):
        """
        Sends data to the e-paper display using the spi_writebyte2 method.
        """
        self.epdconfig.digital_write(self.dc_pin, 1)
        self.epdconfig.digital_write(self.cs_pin, 0)
        self.epdconfig.spi_writebyte2(data)
        self.epdconfig.digital_write(self.cs_pin, 1)

    def read_busy(self):
        """
        Check the status of the e-Paper display and wait if it is busy.

        This method repeatedly sends the "read status" command (0x71) to the display
        and reads the BUSY_PIN to check if the display is busy.
        Once the display is not busy, adds a delay of 20 milliseconds
        to ensure the display is ready for the next operation.

        Note: This method will block the execution of the program
        """
        log.debug("e-Paper display busy")
        self.send_command(0x71)
        busy = self.epdconfig.digital_read(self.busy_pin)
        while busy == 0:
            self.send_command(0x71)
            busy = self.epdconfig.digital_read(self.busy_pin)
        self.epdconfig.delay_ms(20)
        log.debug("e-Paper no longer busy")

    def set_lut(
        self,
        lut_vcom: list[int],
        lut_ww: list[int],
        lut_bw: list[int],
        lut_wb: list[int],
        lut_bb: list[int],
    ) -> None:
        """
        Set the lookup tables (LUT) for voltage levels of the e-ink display.

        This method configures the display's voltages for the common electrode (VCOM)
        and for the different transitions operations:
            white-to-white (WW)
            black-to-white (BW)
            white-to-black (WB)
            black-to-black (BB)
        """
        command_list = [0x20, 0x21, 0x22, 0x23, 0x24]
        lut_list = [lut_vcom, lut_ww, lut_bw, lut_wb, lut_bb]

        for command, lut in zip(command_list, lut_list):
            self.send_command(command)
            for count in lut:
                self.send_data(count)

    def init(self) -> int:
        """
        Initializes the e-paper display.

        This function initializes the display by setting:
         - power
         - VCOM
         - booster
         - OSC
         - panel and resolution settings.
         - It also sets a look-up table for the display.

        If the module initialization fails, it returns -1.
        """

        if self.epdconfig.module_init() != 0:
            return -1
        # EPD hardware init start
        self.reset()

        # self.send_command(0x06)     # btst
        # self.send_data(0x17)
        # self.send_data(0x17)
        # self.send_data(0x28)        # If an exception is displayed, try using 0x38
        # self.send_data(0x17)

        # self.send_command(0x01)   #POWER SETTING
        # self.send_data(0x07)
        # self.send_data(0x07)      #VGH=20V,VGL=-20V
        # self.send_data(0x3f)		#VDH=15V
        # self.send_data(0x3f)		#VDL=-15V

        self.send_command(0x01)  # power setting
        self.send_data(0x17)  # 1-0=11: internal power
        self.send_data(self.Voltage_Frame_7IN5_V2[6])  # VGH&VGL
        self.send_data(self.Voltage_Frame_7IN5_V2[1])  # VSH
        self.send_data(self.Voltage_Frame_7IN5_V2[2])  # VSL
        self.send_data(self.Voltage_Frame_7IN5_V2[3])  # VSHR

        self.send_command(0x82)  # VCOM DC Setting
        self.send_data(self.Voltage_Frame_7IN5_V2[4])  # VCOM

        self.send_command(0x06)  # Booster Setting
        self.send_data(0x27)
        self.send_data(0x27)
        self.send_data(0x2F)
        self.send_data(0x17)

        self.send_command(0x30)  # OSC Setting
        self.send_data(self.Voltage_Frame_7IN5_V2[0])  # 3C=50Hz, 3A=100HZ

        self.send_command(0x04)  # POWER ON
        self.epdconfig.delay_ms(100)
        self.read_busy()

        self.send_command(0x00)  # PANNEL SETTING
        self.send_data(0x3F)  # KW-3f KWR-2F BWROTP-0f BWOTP-1f

        self.send_command(0x61)  # tres
        self.send_data(0x03)  # source 800
        self.send_data(0x20)
        self.send_data(0x01)  # gate 480
        self.send_data(0xE0)

        self.send_command(0x15)
        self.send_data(0x00)

        self.send_command(0x50)  # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x10)
        self.send_data(0x07)

        self.send_command(0x60)  # TCON SETTING
        self.send_data(0x22)

        self.send_command(0x65)  # Resolution setting
        self.send_data(0x00)
        self.send_data(0x00)  # 800*480
        self.send_data(0x00)
        self.send_data(0x00)

        self.set_lut(
            self.LUT_VCOM_7IN5_V2,
            self.LUT_WW_7IN5_V2,
            self.LUT_BW_7IN5_V2,
            self.LUT_WB_7IN5_V2,
            self.LUT_BB_7IN5_V2,
        )
        return 0

    def getbuffer(self, image: Image) -> bytearray:
        """
        Processes PIL Image and returns a bytearray that represents the image data
        The image is converted to monochrome and rotated if necessary
        If dimensions are incorrect, a warning is logged and a blank buffer is returned

        Args:
            image (PIL.Image.Image): The image to process. It should match the width and
            height expected by the display.

        Returns:
            bytearray: A bytearray representing the image data. In this array, 0
            represents white and 1 represents black, following the e-paper display convention.
            If the input image does not have the correct dimensions, a blank buffer is returned.

        Raises:
            If the input is not a valid PIL Image, a TypeError may be raised
            when the function tries to access the `size` attribute or
            call the `convert` or `rotate` methods.
        """
        imwidth, imheight = image.size
        if imwidth == self.width and imheight == self.height:
            image = image.convert("1")
        elif imwidth == self.height and imheight == self.width:
            # image has correct dimensions, but needs to be rotated
            image = image.rotate(90, expand=True).convert("1")
        else:
            log.warning(
                "Incorrect image dimensions, returning blank buffer",
                expected_x=self.width,
                expected_y=self.height,
                actual_x=imwidth,
                actual_y=imheight,
            )
            # return a blank buffer
            return [0x00] * (int(self.width / 8) * self.height)

        buf = bytearray(image.tobytes("raw"))
        # The bytes need to be inverted,
        # PIL Image:   1=white and 0=black
        # e-paper  :   0=white and 1=black
        buf = bytearray(val ^ 0xFF for val in buf)
        return buf

    def display(self, image: bytearray):
        """
        Sends an image to the e-paper display.
        """
        self.send_command(0x13)
        self.send_data2(image)

        self.send_command(0x12)
        self.epdconfig.delay_ms(100)
        self.read_busy()

    def clear(self):
        """
        Clears the e-paper display by setting all pixels to white
        """
        buf = [0x00] * (int(self.width / 8) * self.height)
        self.send_command(0x10)
        self.send_data2(buf)
        self.send_command(0x13)
        self.send_data2(buf)
        self.send_command(0x12)
        self.epdconfig.delay_ms(100)
        self.read_busy()

    def sleep(self):
        """
        Sets the e-paper display to powering off and entering deep sleep
        """
        self.send_command(0x02)  # POWER_OFF
        self.read_busy()

        self.send_command(0x07)  # DEEP_SLEEP
        self.send_data(0xA5)

        self.epdconfig.delay_ms(2000)
        self.epdconfig.module_exit()
