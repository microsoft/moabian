import os
import cv2
from base_camera import BaseCamera


class CameraOpenCV(BaseCamera):
    video_source = 0

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(0)

        s = 512
        b = 32

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, s + b)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, s + b)

        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()
            cropped = img

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', cropped)[1].tobytes()


