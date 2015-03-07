#!/usr/bin/env python
from flask import Flask, render_template, Response, request
import glob

app = Flask(__name__)

i=0
files='abc'

@app.route('/')
def index():
    global files
    files=glob.glob("/home/dlacres/Pictures/Feb29/*.jpg")
    files.sort()
    for x in files:
       print '[%s]\n' % x  
    return render_template('index.html')

@app.route('/command', methods=['GET', 'POST'])
def command():
    global i

    if request.method == 'POST':
        if '>>' in request.form.values():
            i=i+1
            if i>=len(files):
                i=len(files)-1
        elif '<<' in request.form.values():
            i=i-1
            if i<0:
                i=0
        elif '>' in request.form.values():
            while
            i=i+1
            if i>=len(files):
                i=len(files)-1

    return render_template('index.html')

@app.route('/reset_picture', methods=['GET', 'POST'])
def reset():
    global i
    i=2
    return render_template('index.html')


@app.route('/picture_feed')
def picture_feed():
    global i,files
    print '###\n',i,files[i]
    return Response(open(files[i],'rb').read())
    #return Response(gen(),
    #                mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

