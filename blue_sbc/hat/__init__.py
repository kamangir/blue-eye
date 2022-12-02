from abcli.modules import host
import abcli.logging
import logging

logger = logging.getLogger(__name__)

NAME = "blue_sbc.hat"

from .hat import *
from .grove import *
from .led_switch import *


hat = (
    Grove_Hat()
    if cookie.get("hat.type", "else") == "grove"
    else RPi_Led_Switch_Hat()
    if host.is_rpi()
    else Jetson_Led_Switch_Hat()
    if host.is_jetson()
    else Hat()
)

logger.info(f"{NAME}: hat: {hat.__class__.__name__}")
