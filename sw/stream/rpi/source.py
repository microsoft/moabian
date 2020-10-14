#!/usr/bin/env python3
import time
import imagezmq
from imutils.video import VideoStream

sender = imagezmq.ImageSender(connect_to='tcp://localhost:5555')

picam = VideoStream(usePiCamera=True).start()
time.sleep(0.5)
while True:
    image = picam.read()
    sender.send_image("moab", image)
