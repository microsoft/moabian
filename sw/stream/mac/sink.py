#!/usr/bin/env python3
import sys
import cv2
import traceback
import imagezmq
import numpy as np
from imutils.video import FPS

print('Listening')

try:
    with imagezmq.ImageHub() as hub:

        counter = 0
        first_image = True

        while True:
            #sent_from, jpg_buffer = hub.recv_image()
            sent_from, jpg= hub.recv_jpg()

            if first_image:
                fps = FPS().start()
                first_image = False
            fps.update()
            counter += 1

            #array = np.frombuffer(jpg_buffer, dtype=np.uint8)
            arr = np.frombuffer(jpg, dtype='uint8')
            image = cv2.imdecode(arr, -1)

            cv2.imshow(sent_from, image) # 1 window for each rpi
            cv2.waitKey(1)
            hub.send_reply(b'ok')

except (KeyboardInterrupt, SystemExit):
    pass
except Exception as ex:
    print('Traceback:', ex)
    traceback.print_exc()
finally:

    print(f'Frames received: {counter}')
    if first_image:
        sys.exit()

    fps.stop()
    image_size = image.shape
    uncomp = image_size[0] * image_size[1] * image_size[2]

    print(f"Last image shape:  {image_size}")
    print(f"Uncompressed size: {uncomp}")
    print(f"Elapsed time: {fps.elapsed():.2f}")
    print(f"FPS: {fps.fps():.2f}\n")

    cv2.destroyAllWindows()
    hub.close()
    sys.exit()

