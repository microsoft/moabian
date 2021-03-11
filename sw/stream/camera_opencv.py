import os
import cv2
from base_camera import BaseCamera


class CameraOpenCV(BaseCamera):

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(0)

        # Ask opencv to capture in the native aspect ratio of 4:3
        # AND capture on a 4-bit boundary
        w = 384
        h = 288

        # Our final "destination" rectangle is 256x256
        d = 256

        x = int((w / 2 - d / 2))
        y = int((h / 2 - d / 2))

        # TODO: See if these x/y offsets are universal across Mark 2 & 3
        x += -12
        y +=  4

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        camera.set(cv2.CAP_PROP_FPS, 30)

        camera.set(cv2.CAP_PROP_BRIGHTNESS, 60)
        camera.set(cv2.CAP_PROP_CONTRAST, 100)

        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            cropped = img[y:y+d, x:x+d]
            yield cv2.imencode('.jpg', cropped)[1].tobytes()
