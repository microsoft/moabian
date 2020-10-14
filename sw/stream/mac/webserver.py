#!/usr/bin/env python3
import cv2
import sys
import imagezmq
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

def sendImagesToWeb():
    receiver = imagezmq.ImageHub(open_port='tcp://localhost:5566', REQ_REP = False)
    while True:
        camName, frame = receiver.recv_image()
        jpg = cv2.imencode('.jpg', frame)[1]
        yield b'--frame\r\nContent-Type:image/jpeg\r\n\r\n'+jpg.tostring()+b'\r\n'

@Request.application
def application(request):
    print("got request")
    return Response(sendImagesToWeb(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    run_simple('127.0.0.1', 4000, application)
