#!/usr/bin/env python3

import os
import socket
from flask import Flask, render_template, Response, url_for, redirect

from camera_file import CameraFile
from camera_opencv import CameraOpenCV

app = Flask(__name__,
        static_url_path='',
        static_folder='static',
        template_folder='templates')

@app.route('/')
def default():
    return redirect(url_for('static', filename='file.html'))

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/file_mjpeg')
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
    print(f" • Moab View      http://{ip}:{port}/file.html")
    print(f" • OpenCV View    http://{ip}:{port}/opencv.html")
    app.run(host=ip, port=port, threaded=True)


