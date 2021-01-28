import os
import cv2
from base_camera import BaseCamera


class CameraNative(BaseCamera):
    video_source = 0

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(0)

        w = 512
        h = 512

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        camera.set(cv2.CAP_PROP_FPS, 30)

        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
