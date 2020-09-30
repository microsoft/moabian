#!/usr/bin/env python3
import sys
import cv2
import time
import imagezmq
import traceback
import numpy as np
from imutils.video import VideoStream

jpg_quality = 90

try:
    sender = imagezmq.ImageSender(connect_to='tcp://192.168.1.128:5555')
    #picam = VideoStream(usePiCamera=True, resolution=(512,512)).start()
    picam = VideoStream(resolution=(512,512)).start()
    time.sleep(0.2)  # allow camera sensor to warm up

    while True:  # send images as stream until Ctrl-C
        image = picam.read()
        ret_code, jpg_buffer = cv2.imencode(".jpg", image,
                [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])
        response = sender.send_jpg("source", jpg_buffer)
except (KeyboardInterrupt, SystemExit):
    pass  # Ctrl-C was pressed to end program
except Exception as ex:
    print('Traceback error:', ex)
    traceback.print_exc()
finally:
    picam.stop()
    sys.exit()
