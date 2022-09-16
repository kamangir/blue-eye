import cv2
import time
from blue_sbc.screen.classes import Screen


class Scroll_Phat_HD(Screen):
    def __init__(self):
        super(Scroll_Phat_HD, self).__init__()
        self.size = (7, 17)
        self.animated = True

    def show(self, image, session=None, header=[], sidebar=[]):
        import scrollphathd

        image_ = cv2.resize(
            cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY,
            ),
            self.size,
        )

        super(Scroll_Phat_HD, self).show(image_, session, header, sidebar)

        for x in range(0, 17):
            for y in range(0, 7):
                scrollphathd.set_pixel(x, y, image_[x, y])

        time.sleep(0.01)
        scrollphathd.show()

        return self
