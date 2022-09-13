import cv2
from PIL import Image
import time
from blue_sbc.screen.classes import Screen


class Adafruit_Rgb_Matrix(Screen):
    def __init__(self):
        super(Adafruit_Rgb_Matrix, self).__init__()
        self.size = (32, 32)

        from rgbmatrix import RGBMatrix, RGBMatrixOptions

        options = RGBMatrixOptions()
        options.rows = 32
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = "adafruit-hat"  # adafruit-hat/regular

        self.matrix = RGBMatrix(options=options)

    def show(
        self,
        image,
        session,
        header=[],
        sidebar=[],
    ):
        super(Adafruit_Rgb_Matrix, self).show(image, session, header, sidebar)

        self.matrix.SetImage(
            Image.fromarray(cv2.resize(image, self.size)).convert("RGB")
        )

        return self