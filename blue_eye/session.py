from abcli.modules.hardware import instance as hardware
from abcli.modules.host.session import COOKIE
from abcli.modules.host.session import Session
from abcli.plugins.storage import instance as storage
from abcli.modules import terraform


class Blue_Eye_Session(Session):
    def __init__(self):
        super(Blue_Eye_Session, self).__init__()

        self.capture_command = ""

        self.new_frame = False
        self.frame_image = terraform.poster(None)
        self.frame_filename = ""

        self.timer = {}
        for name, period in {
            "capture": 60 * 5,
        }.items():
            self.add_timer(name, period)

        self.auto_upload = COOKIE.get("host.session.auto_upload", True)
        self.outbound_queue = COOKIE.get("host.session.outbound_queue", "stream")
        self.do_annotate = COOKIE.get("host.session.capture.annotate", True)
        self.capture_enabled = COOKIE.get("host.session.capture.enabled", True)

    def check_camera(self):
        self.new_frame = False

        if not self.capture_command or not self.capture_enabled:
            return

        success, filename, image = camera.capture(self.capture_command)

        self.capture_command = ""

        if not filename or filename == "same" or not success:
            return

        hardware.pulse(hardware.data_pin)

        self.new_frame = True
        self.frame_image = image
        self.frame_filename = filename

        if self.do_annotate:
            camera.annotate()

        if self.outbound_queue:
            from abcli.plugins.message import Message

            Message(
                filename=self.frame_filename,
                recipient=self.outbound_queue,
                subject="frame",
            ).submit()
        elif self.auto_upload:
            storage.upload_file(self.frame_filename)