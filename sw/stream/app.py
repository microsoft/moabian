#!/usr/bin/env python
import os
import socket
from flask import Flask, render_template, Response

from camera_file import Camera

app = Flask(__name__, template_folder='.')


@app.route('/')
def index():
    return render_template('index.html', title='Moab Camera')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video')
def video():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)






@Request.application
def application(request):
    print("got request")
    d = Headers()
    d.add('Connection', 'close')
    d.add('Age', 0)
    d.add('Cache-Control', 'no-cache,no-store,must-revalidate,pre-check=0,post-check=0,max-age=0')
    d.add('Pragma', 'no-cache')
    d.add('Server', 'Moab v2.5')
    #d.add('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
    #return Response(sendImagesToWeb(), headers=d)
    return Response(sendImagesToWeb(), headers=d, mimetype='multipart/x-mixed-replace; boundary=frame')

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
