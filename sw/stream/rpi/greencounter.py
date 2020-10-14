#!/usr/bin/env python3
import sys
import cv2
import time
import imagezmq
import traceback
import numpy as np
from imutils.video import VideoStream

dest_uri="tcp://localhost:5555"
jpg_quality = 50
i = 0

try:
    sender = imagezmq.ImageSender(connect_to=dest_uri)

    while True:
        i = i + 1

        # Create a simple image
        image = np.zeros((400, 400, 3), dtype='uint8')
        green = (0, 255, 0)
        cv2.rectangle(image, (50, 50), (300, 300), green, 5)

        # Add an incrementing counter to the image
        cv2.putText(image, str(i), (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 4)

        #ret_code, jpg_buffer = cv2.imencode(".jpg", image,
        #        [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])

        #response = sender.send_jpg("moab", jpg_buffer)
        response = sender.send_image("moab", image)

except (KeyboardInterrupt, SystemExit):
    pass  # Ctrl-C was pressed to end program
except Exception as ex:
    print('Python error with no Exception handler:')
    print('Traceback error:', ex)
    traceback.print_exc()
finally:
    sys.exit()

