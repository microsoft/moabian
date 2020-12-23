#!/usr/bin/env python
import os
import socket
from flask import Flask, render_template, Response

from camera_file import CameraFile
from camera_opencv import CameraOpenCV

app = Flask(__name__, template_folder='.')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/opencv')
def raw():
    return render_template('opencv.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_mjpeg')
def video_mjpeg():
    return Response(gen(CameraFile()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/opencv_mjpeg')
def opencv_mjpeg():
    return Response(gen(CameraOpenCV()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def getHostIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('1.1.1.1', 1))
    local_ip = s.getsockname()[0]
    return local_ip

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    hostname = socket.gethostname()

    ip = getHostIP()
    print(f"Moab main.py stream  http://{ip}:{port}/")
    print(f"Native OpenCV stream http://{ip}:{port}/opencv")
    app.run(host=ip, port=port, threaded=True)
