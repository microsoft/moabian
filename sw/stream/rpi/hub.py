#!/usr/bin/env python3
import cv2
import imagezmq

hub = imagezmq.ImageHub()
stream_monitor = imagezmq.ImageSender(connect_to='tcp://*:5566', REQ_REP = False)

while True:
    name, image= hub.recv_image()
    hub.send_reply(b'OK')
    stream_monitor.send_image(name, image)
