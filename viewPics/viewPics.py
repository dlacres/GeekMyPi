#!/usr/bin/env python
from flask import Flask, render_template, Response, request
import glob,time
from collections import defaultdict

app = Flask(__name__)

i=0
files='abc'
isPlay=False
isBack=False
stepForward=False
stepBackward=False
numberString = '000'
clips = defaultdict(list)
currentClip=0
currentIndex=0

@app.route('/')
def index():
    global files, clips, currentClip, currentIndex
    files=glob.glob("/home/dlacres/Pictures/Feb29/*.jpg")
    files.sort()

    for f in files:
        numberString = int(f[-25:-22])
        clips[numberString].append(f)

    currentClip=min(clips.keys())
    currentIndex=0
    print currentClip
    print clips.keys()
    return render_template('index.html')

@app.route('/command', methods=['GET', 'POST'])
def command():
    global i, isPlay, isBack, stepForward, stepBackward

    isPlay=False
    isBack=False
    stepForward=False
    stepBackward=False

    if request.method == 'POST':
        if '>>' in request.form.values():
            stepForward=True
        elif '<<' in request.form.values():
            stepBackward=True
        elif '>' in request.form.values():
            isPlay=True
        elif '<' in request.form.values():
            isBack=True
        elif '||' in request.form.values():
            i=0
  
    return render_template('index.html')

@app.route('/reset_picture', methods=['GET', 'POST'])
def reset():
    global i
    i=2
    return render_template('index.html')


def gen(stringNumber):
    global i, isPlay, isBack, clips

    if isPlay:
        frames=clips[stringNumber]
    else:
        frames=reversed(clips[stringNumber])

    for frame in frames:
        time.sleep(.1)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open(frame,'rb').read() + b'\r\n')


@app.route('/picture_feed')
def picture_feed():
    global i,files, isPlay, iBack, currentClip, currentIndex

    if isPlay:
        currentClip=next((key for key in sorted(clips.keys()) if key > currentClip),currentClip)
        response=Response(gen(currentClip),mimetype='multipart/x-mixed-replace; boundary=frame')
        currentIndex=0
        return response
    elif isBack:
        currentClip=next((key for key in reversed(sorted(clips.keys())) if key < currentClip),currentClip)
        response=Response(gen(currentClip),mimetype='multipart/x-mixed-replace; boundary=frame')
        currentIndex=0
        return response
    elif stepForward:
        currentIndex=currentIndex+1
        if currentIndex==len(clips[currentClip]):
            currentClip=next((key for key in sorted(clips.keys()) if key > currentClip),currentClip)
            currentIndex=0
        response = Response(open(clips[currentClip][currentIndex],'rb').read())

        return response
    elif stepBackward:
        currentIndex=currentIndex-1
        if currentIndex==len(clips[currentClip]):
            currentClip=next((key for key in reversed(sorted(clips.keys())) if key < currentClip),currentClip)
            currentIndex=0
        response = Response(open(clips[currentClip][currentIndex],'rb').read())

        return response
        

    print 'Clip %s index %s' % (currentClip,currentIndex)
    print clips[currentClip]
    return Response(open(clips[currentClip][currentIndex],'rb').read())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

