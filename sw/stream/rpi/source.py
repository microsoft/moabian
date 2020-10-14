#!/usr/bin/env python3
import time
import imagezmq
from imutils.video import VideoStream

import cv2

sender = imagezmq.ImageSender(connect_to='tcp://localhost:5555')

picam = VideoStream(usePiCamera=True, resolution=(512,512), framerate=24).start()
time.sleep(0.5)
while True:
    image = picam.read()

    # since this code will run in the MQDecorator moab/control container
    # we might want to do the JPEG compression on the hub.py side to offload work
    # to the other container. That would mean sending the raw image instead.

    ret_code, jpg_buf = cv2.imencode(".jpg", image,
        [int(cv2.IMWRITE_JPEG_QUALITY), 50])

    #sender.send_image("moab", image)
    sender.send_image("moab", jpg_buf)
