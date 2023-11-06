import cv2
import numpy as np
import time

# from matrix_emulator import Matrix
from matrix_driver import Matrix
from streamer import Streamer

config = {
    "size": (96, 48),
    "url": "https://www.youtube.com/watch?v=60xdyUIlPGQ",
    "adjustments": {
        "whitepoint": [240, 240, 240],
        "blackpoint": [30, 30, 30],
        "saturation": 1.2,
        "temperature": -0.03,
    },
    "crop": [35, 8, 100, 70],
}

BLANK_FRAME = np.zeros((48, 96, 3), dtype=np.uint8)
STARTUP_FRAME = cv2.imread("/home/dietpi/simple_matrix_stream/startup.png")
# STARTUP_FRAME = cv2.imread("startup.png")

if __name__ == '__main__':
    matrix = Matrix()
    streamer = Streamer(config["url"], size=config["size"], adjustments=config["adjustments"], crop=config["crop"])

    matrix.set_pixels(BLANK_FRAME)
    matrix.reset()
    time.sleep(0.5)
    matrix.set_pixels(STARTUP_FRAME)
    time.sleep(5)

    streamer.start()
    while True:
        frame = streamer.get_frame()
        matrix.set_pixels(frame)
