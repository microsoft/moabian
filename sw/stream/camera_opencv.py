import os
import cv2
from base_camera import BaseCamera


class CameraOpenCV(BaseCamera):
    video_source = 0

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 512)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
