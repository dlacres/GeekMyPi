#!/usr/bin/env python
from flask import Flask,render_template, Response, request
import glob,time,shutil,os
from collections import defaultdict

app = Flask(__name__)

#ret=subprocess.call('ping -c 1 192.168.1.108',shell=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT)

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
mySize=0
response=0

def getName(s):
    for c in s:
        if c=='/':
            s=''
        else:
            s=s+c
    return s

def getIndex(s):
    numDayStr = s[-15:-13]
    if s[-25:-24]=='/' or s[-25:-24]=='_' or s[-25:-24]=='-':
        numIdxStr = s[-24:-22]
        numCamStr = s[-27:-25]
    else:
        numIdxStr = s[-25:-22]
        numCamStr = s[-28:-26]
    numStr=numCamStr+numIdxStr+numDayStr
    print numStr
    return int(numStr)

def getClipName(): 
    global clips
    t=clips[currentClip][0]
    if t[-25:-24]=='/' or t[-25:-24]=='_' or t[-25:-24]=='-':
        clipName=t[-24:-22]+' '+t[-17:-15]+'-'+t[-15:-13]+' '+t[-13:-11]+':'+t[-11:-9]+' ['+str(len(clips[currentClip]))+']'
    else:
        clipName=t[-25:-22]+' '+t[-17:-15]+'-'+t[-15:-13]+' '+t[-13:-11]+':'+t[-11:-9]+' ['+str(len(clips[currentClip]))+']'
    return clipName

@app.route('/')
def index():
    global files, clips, currentClip, currentIndex, mySize
    files=glob.glob("/home/dlacres/tmp/*.jpg")
    files.sort()
    for f in files:
        numberString=getIndex(f)
        clips[numberString].append(f)
        print "File %s, number %d" % (f,numberString)

    currentClip=min(clips.keys())

    currentIndex=0

    templateData = {
      'mySize': mySize,
      'clipName' : getClipName()
      }
    return render_template('index.html', **templateData)

#    return render_template('index.html')

@app.route('/command', methods=['GET', 'POST'])
def command():
    global guiCmd, mySize, guiCmdOld, currentClip, currentIndex, response, clips

    if request.method == 'POST':
        if 'sf' in request.form.values():
            guiCmd=0 #Step Forward
        elif 'sb' in request.form.values():
            guiCmd=1 #Step Backward
        elif '>' in request.form.values():
            guiCmd=2 #Play Forward
        elif '<' in request.form.values():
            guiCmd=3 #Play Backward
        elif 'siz' in request.form.values():
            guiCmd=4
            if mySize==0:
                mySize=1
            elif mySize==1:
                mySize=2
            elif mySize==2:
                mySize=0
        elif 'sav' in request.form.values():
            guiCmd=5
        elif 'delAll' in request.form.values():
            guiCmd=6

    if guiCmd==0:#forward one Pic
        currentIndex=currentIndex+1
        if currentIndex==len(clips[currentClip]):
            currentClip=next((key for key in sorted(clips.keys()) if key > currentClip),currentClip)
            currentIndex=0
        response = Response(open(clips[currentClip][currentIndex],'rb').read())
    elif guiCmd==1:#back one Pic
        currentIndex=currentIndex-1
        if currentIndex==len(clips[currentClip]):
            currentClip=next((key for key in reversed(sorted(clips.keys())) if key < currentClip),currentClip)
            currentIndex=0
        response = Response(open(clips[currentClip][currentIndex],'rb').read())
    elif guiCmd==2: #play one clip
        if guiCmd==guiCmdOld:
            currentClip=next((key for key in sorted(clips.keys()) if key > currentClip),currentClip)
        response=Response(gen(currentClip),mimetype='multipart/x-mixed-replace; boundary=frame')
        currentIndex=0
    elif guiCmd==3:#back one clip
        if guiCmd==guiCmdOld:
            currentClip=next((key for key in reversed(sorted(clips.keys())) if key < currentClip),currentClip)
        response=Response(gen(currentClip),mimetype='multipart/x-mixed-replace; boundary=frame')
        currentIndex=0
    elif guiCmd==4:#Change Pic Size
        response = Response(open(clips[currentClip][currentIndex],'rb').read())
    elif guiCmd==5:#Save Pic
        files=clips[currentClip]
        for f in files:
            name=getName(f)
            print "Name %s File %s" % (name,f)
            #newFile='/home/dlacres/pic/+name'
            #print newFile
            shutil.copyfile(f,'/home/dlacres/pic/'+name)
    elif guiCmd==6:#Delete All Pictures
        for key in sorted(clips.keys()):
            files=clips[key]
            for file in files:
                os.remove(file)
        

    guiCmdOld=guiCmd                
    print 'Clip %s index %s' % (currentClip,currentIndex)

    templateData = {
      'mySize': mySize,
      'clipName' : getClipName()
      }

    print templateData
    return render_template('index.html', **templateData)

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
    global response

    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

