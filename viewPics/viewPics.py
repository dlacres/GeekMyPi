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
guiCmd=0
guiCmdOld=4

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
    global guiCmd

    if request.method == 'POST':
        if '>>' in request.form.values():
            guiCmd=0 #stepForward=True
        elif '<<' in request.form.values():
            guiCmd=1 #stepBackward=True
        elif '>' in request.form.values():
            guiCmd=2 #isPlay=True
        elif '<' in request.form.values():
            guiCmd=3 #isBack=True
        elif '||' in request.form.values():
            guiCmd=4
  
    return render_template('index.html')

def gen(stringNumber):
    global guiCmd, isPlay, isBack, clips

    if guiCmd==2: #Play
        frames=clips[stringNumber]
    else:         #Backward Play
        frames=reversed(clips[stringNumber])

    for frame in frames:
        time.sleep(.1)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open(frame,'rb').read() + b'\r\n')


@app.route('/picture_feed')
def picture_feed():
    global guiCmd, guiCmdOld, currentClip, currentIndex

    if guiCmd==2: #play one clip
        if guiCmd==guiCmdOld:
            currentClip=next((key for key in sorted(clips.keys()) if key > currentClip),currentClip)
        print currentClip
        response=Response(gen(currentClip),mimetype='multipart/x-mixed-replace; boundary=frame')
        currentIndex=0
        #return response
    elif guiCmd==3:#back one clip
        if guiCmd==guiCmdOld:
            currentClip=next((key for key in reversed(sorted(clips.keys())) if key < currentClip),currentClip)
        print currentClip
        response=Response(gen(currentClip),mimetype='multipart/x-mixed-replace; boundary=frame')
        currentIndex=0
        #return response
    elif guiCmd==0:#forward one Pic
        currentIndex=currentIndex+1
        if currentIndex==len(clips[currentClip]):
            currentClip=next((key for key in sorted(clips.keys()) if key > currentClip),currentClip)
            currentIndex=0
        print currentClip
        response = Response(open(clips[currentClip][currentIndex],'rb').read())

        #return response
    elif guiCmd==1:#back one Pic
        currentIndex=currentIndex-1
        if currentIndex==len(clips[currentClip]):
            currentClip=next((key for key in reversed(sorted(clips.keys())) if key < currentClip),currentClip)
            currentIndex=0
        print currentClip
        response = Response(open(clips[currentClip][currentIndex],'rb').read())

        #return response

    guiCmdOld=guiCmd                
    print guiCmd
    # Pause one pick
    print 'Clip %s index %s' % (currentClip,currentIndex)
    return response
    #print clips[currentClip]
    #return Response(open(clips[currentClip][currentIndex],'rb').read())


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

