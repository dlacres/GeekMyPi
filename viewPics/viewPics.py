#!/usr/bin/env python
from flask import Flask, render_template, Response
import glob

app = Flask(__name__)

i=0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset_picture')
def reset():
    global i
    i=0
    return render_template('index.html')

def gen():
    global i
    filter="*.jpg"
    files=glob.glob("/home/dlacres/Pictures/"+filter)
    files.sort
    frames=[open(f,'rb').read() for f in files]
    length = len(frames)
    while True:
        i=i+1
        if (i >= length):
            i=length
        if (i < 0):
            i=0
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frames[i-1] + b'\r\n')

@app.route('/picture_feed')
def picture_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

