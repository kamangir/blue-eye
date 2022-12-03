import cv2
from blue_sbc.screen.classes import Screen
from grove.grove_button import GroveButton
from abcli import string
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from abcli import logging
import logging

logger = logging.getLogger(__name__)

BUTTON = 24

RST = None  # on the PiOLED this pin isnt used


class Grove_Screen(Screen):
    def __init__(self):
        super(Grove_Screen, self).__init__()
        # https://wiki.seeedstudio.com/Grove-OLED_Display_0.96inch/
        self.size = (64, 128)

        self.button = GroveButton(BUTTON)
        self.button.on_press = lambda t: grove_button_on_press(self, t)
        self.button.on_release = lambda t: grove_button_on_release(self, t)

        # https://github.com/IcingTomato/Seeed_Python_SSD1315/blob/master/examples/stats.py
        self.display = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

        self.display.begin()
        self.display.clear()
        self.display.display()

        self.image = Image.new(
            "1",
            (self.display.width, self.display.height),
        )

        self.draw = ImageDraw.Draw(self.image)

        # Draw a black filled box to clear the image.
        self.draw.rectangle(
            (0, 0, self.display.width, self.display.height),
            outline=0,
            fill=0,
        )

        self.padding = -2
        self.top = self.padding
        self.bottom = self.display.height - self.padding

        self.font = ImageFont.load_default()

    def show(self, image, session=None, header=[], sidebar=[]):
        self.draw.rectangle(
            (0, 0, self.display.width, self.display.height),
            outline=0,
            fill=0,
        )
        for index in range(min(4, len(header))):
            self.draw.text(
                (0, self.top + 8 * index),
                header[index],
                font=self.font,
                fill=255,
            )

        self.display.image(self.image)
        self.display.display()

        return self


def grove_button_on_press(screen, t):
    logger.info("grove.button: pressed.")


def grove_button_on_release(screen, t):
    logger.info(f"grove.button: released after {string.pretty_duration(t)}.")

    if t > 10:
        key = "s"
    elif t > 3:
        key = "u"
    else:
        key = " "

    screen.key_buffer.append(key)
    logger.info(f"{screen.__class__.__name__}: '{key}'")
