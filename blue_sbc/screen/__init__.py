from abcli.modules.cookie import cookie
import abcli.logging
import logging

logger = logging.getLogger(__name__)

NAME = "blue_sbc.screen"

screen_name = cookie.get("session.screen", "display")
if screen_name == "adafruit_rgb_matrix":
    from .adafruit_rgb_matrix import instance as screen
elif screen_name == "scroll_phat_hd":
    from .scroll_phat_hd import instance as screen
elif screen_name == "template":
    from .template import instance as screen
elif screen_name == "unicorn_16x16":
    from .unicorn_16x16 import instance as screen
else:
    from .display import instance as screen

logger.info(f"{NAME}: screen: {screen.__class__.__name__}")
