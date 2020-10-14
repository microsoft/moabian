#!/usr/bin/env python3
import os
import cv2
import sys
import socket
import imagezmq
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

def sendImagesToWeb():
    receiver = imagezmq.ImageHub(open_port='tcp://localhost:5566', REQ_REP = False)
    while True:
        camName, jpg = receiver.recv_jpg()
        yield b'--frame\r\nContent-Type:image/jpeg\r\n\r\n'+jpg+b'\r\n'

@Request.application
def application(request):
    print("got request")
    return Response(sendImagesToWeb(), mimetype='multipart/x-mixed-replace; boundary=frame')

def getHostIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('1.1.1.1', 1))
    local_ip = s.getsockname()[0]
    return local_ip

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    hostname = socket.gethostname()

    ip = getHostIP()
    print(f"Open browser to http://{ip}:{port}")
    run_simple(ip, port, application)

# source.py (MQDecorator in Control) -->
# sink.py ==> web container: listening to everyone (
# web container publishes the data on index.html (via mpeg) over port 8000
