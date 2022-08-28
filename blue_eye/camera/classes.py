import argparse
import cv2
import numpy as np
import os
from time import sleep
from abcli.modules import objects
from abcli.plugins.display import instance as display
from abcli import file
from abcli.modules.hardware import instance as hardware
from abcli.modules import host
from abcli.plugins import graphics
from abcli import string
from . import NAME
from .constants import *
from blue_eye.algo.diff import Diff
from abcli.logging import crash_report
from abcli import logging
import logging

logger = logging.getLogger(__name__)


class Imager(object):
    def __init__(self):
        self.frame = -1
        self.unique_frame = -1

        self.object_name = os.getenv("abcli_object_name", "")
        self.object_folder = os.getenv("abcli_object_folder", "")

        self.diff = Diff(host.cookie.get("camera.diff", 0.1))

    def capture(self):
        self.frame += 1
        return False, "", np.ones((1, 1, 3), dtype=np.uint8) * 127

    def filename_of(
        self,
        filename="",
        name_and_extension="camera.jpg",
    ):
        """produce filename.

        Args:
            filename           : filename. Default to "".
            name_and_extension : name and extension. Default to "camera.jpg".

        Returns:
            str: filename
        """
        if "filename" == "-":
            return ""

        filename = (
            filename
            if filename
            else os.path.join(
                self.object_folder,
                "Data",
                str(self.frame),
                name_and_extension,
            )
        )

        file.prepare_for_saving(filename)

        return filename

    def signature(self, image):
        return [
            " | ".join(
                objects.signature(self.frame)
                + [
                    string.pretty_shape_of_matrix(image),
                    self.__class__.__name__.lower(),
                ]
                + self.signature_()
            ),
            " | ".join(host.signature()),
        ]

    def signature_(self):
        return []


class TemplateImager(Imager):
    def __init__(self):
        pass

    def capture(self, filename="", sign=True):
        """capture.

        Args:
            filename (str, optional): filename. Defaults to "": use timestamp.
            sign (bool, optional): sign output. Defaults to True.

        Returns:
            bool: success.
        """
        _, _, image_blank = super(TemplateImager, self).capture()

        filename = self.filename_of(filename)

        return False, filename, image_blank

    def signature_(self):
        return ["device_name"]


class Camera(Imager):
    def __init__(self):
        super(Camera, self).__init__()

        self.rotation = host.cookie.get("camera.rotation", 0)
        self.hi_res = host.cookie.get("camera.hi_res", True)
        self.device = None

        self.resolution = []

    def capture(
        self,
        close_after=True,
        filename="",
        forced=False,
        log=True,
        open_before=True,
        save=True,
        sign=True,
    ):
        """capture.

        Args:
            close_after (bool, optional): close camera after capture. Defaults to True.
            filename (str, optional): filename. Defaults to True.
            forced (bool, optional): forced capture. Defaults to False.
            log (bool, optional): log. Defaults to True.
            open_before (bool, optional): open the camera before capture. Defaults to True.
            save (bool, optional): save the image. Defaults to True.
            sign (bool, optional): sign the image. Defaults to True.

        Returns:
            bool: success.
            str: filename.
            image: np.ndarray.
        """
        success, filename, image = super(Camera, self).capture()

        if open_before:
            if not self.open():
                return success, filename, image

        if self.device is None:
            return success, filename, image

        if host.is_rpi():
            temp = file.auxiliary(self, "png")
            try:
                self.device.capture(temp)
                success = True
            except:
                crash_report(f"{NAME}.capture() failed")

            if success:
                success, image = file.load_image(temp)
        else:
            try:
                success, image = self.device.read()

                if success:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            except:
                crash_report(f"{NAME}.capture() failed")

        if close_after:
            self.close()

        if success and not forced:
            if self.diff.same(image):
                return True, "same", None

        self.unique_frame += 1

        if success and sign:
            image = graphics.add_signature(image, [], self.signature(image))

        if success and save:
            filename = self.filename_of(filename)

            if filename:
                success = file.save_image(filename, image)

        if success and log:
            logger.info(
                "camera.capture({}): {}{}".format(
                    "forced" if forced else "",
                    f"{filename} - " if filename else "",
                    string.pretty_shape_of_matrix(image),
                )
            )

        return success, filename, image

    # https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/6
    def capture_video(self, filename, length, options=""):
        """capture video.

        Args:
            filename (str): filename.
            length (int): in seconds.
            options (str, optional): options.
                preview : show preview. Defaults to True.
                pulse   : pulse. Default to True.

        Returns:
            bool: success
        """
        options = Options(options).default("preview", True).default("pulse", True)

        if not host.is_rpi:
            logger.error("capture.capture_video() works on rpi.")
            return False

        if not self.open(options):
            return False

        success = True
        try:
            if options["preview"]:
                self.device.start_preview()

            self.device.start_recording(filename)
            if options["pulse"]:
                for _ in range(int(10 * length)):
                    hardware.pulse("outputs")
                    sleep(0.1)
            else:
                sleep(length)
            self.device.stop_recording()

            if options["preview"]:
                self.device.stop_preview()
        except:
            crash_report(f"{NAME}.capture_video()")
            success = False

        if not self.close():
            return False

        if success:
            logger.info(
                "{}.capture_video(): {} -{}-> {}".format(
                    NAME,
                    string.pretty_duration(length),
                    string.pretty_bytes(file.size(filename)),
                    filename,
                )
            )

        return success

    def close(self, log=False):
        """close camera.

        Args:
            log (bool, optional): log. Defaults to False.

        Returns:
            bool: success
        """

        if self.device is None:
            logger.warning(f"{NAME}.close(): device is {self.device}, failed.")
            return False

        success = False
        try:
            if host.is_rpi():
                self.device.close()
            else:
                self.device.release()
            success = True
        except:
            crash_report(f"{NAME}.close() failed")
            return False

        self.device = None

        if log:
            logger.info(f"{NAME}.close()")

        return success

    def get_resolution(self):
        try:
            if host.is_rpi():
                from picamera import PiCamera

                return [value for value in self.device.resolution]
            else:
                return [
                    int(self.device.get(const))
                    for const in [cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FRAME_WIDTH]
                ]
        except:
            crash_report("camera.get_resolution() failed")
            return []

    def open(
        self,
        log=True,
        resolution=None,
    ):
        """open camera.

        Args:
            log (bool, optional): log. Defaults to True.
            resolution (Tuple(int,int), optional): resolution. Defaults to None.

        Returns:
            bool: success.
        """
        try:
            if host.is_rpi():
                from picamera import PiCamera

                self.device = PiCamera()
                self.device.rotation = int(self.rotation)

                # https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/7
                self.device.resolution = (
                    ((2592, 1944) if self.hi_res else (728, 600))
                    if resolution is None
                    else resolution
                )
            else:
                self.device = cv2.VideoCapture(0)

                # https://stackoverflow.com/a/31464688
                self.device.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)
                self.device.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)

            self.resolution = self.get_resolution()

            if log:
                logger.info(f"{NAME}.open({string.pretty_shape(self.resolution)})")

            return True
        except:
            crash_report(f"{NAME}.open: failed.")
            return False

    def signature_(self):
        return [
            "diff: {:.03f} - {}".format(
                self.diff.last_diff,
                string.pretty_duration(self.diff.last_same_period, "largest,ms,short"),
            ),
        ]
