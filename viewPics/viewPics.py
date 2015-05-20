#!/usr/bin/env python
from flask import Flask,render_template, Response, request
import glob,time,shutil,os
from collections import defaultdict

app = Flask(__name__)

#ret=subprocess.call('ping -c 1 192.168.1.108',shell=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT)
# Motion %cam_%Y_%m_%d_%v_%H_%M_%S_%q

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
#response=0
#cam=''
#month=''
#day=''
#year=''
#hour=''
#min=''
#sec=''
#seq=''

def getName(s):
    global cam,year,month,day,seq,hour,min,sec,num
    for c in s:
        if c=='/':
            s=''
        else:
            s=s+c
    return s


def splitString(s):
  idx=0
  astr=''
  listStr=['']

  for c in s:
    if c=='_' or c=='.':
      listStr.append(aStr)
      aStr=''
    else:
      if c=='/':
        aStr=''
      else:
        aStr=aStr+c
  listStr.append(aStr)

  return listStr

# cam year month day seq hour min sec num
# 1   2    3     4   5   6    7   8   9

def getIndex(s):
    num=0

    l=splitString(s)

    #      cam  mon  day
    numStr=l[1]+l[3]+l[4]
    try:
        num=int(numStr)
    except ValueError:
        print 'ERROR 1'
    return num

def getClipName(s,listLen): 
    monStr='ERR'

    l=splitString(s)

    month=l[3]
    if month=='01': monStr='Jan'
    if month=='02': monStr='Feb'
    if month=='03': monStr='Mar'
    if month=='04': monStr='Apr'
    if month=='05': monStr='May'
    if month=='06': monStr='Jun'
    if month=='07': monStr='Jul'
    if month=='08': monStr='Aug'
    if month=='09': monStr='Sep'
    if month=='10': monStr='Oct'
    if month=='11': monStr='Nov'
    if month=='12': monStr='Dec'

    clipName='['+l[5]+'] '+monStr+','+l[4]+','+l[2]+' '+l[6]+':'+l[7]+':'+l[8]+' ['+str(listLen)+']'

    return clipName

@app.route('/')
def index():
    global files, clips, currentClip, currentIndex, mySize, response
    files=glob.glob("/home/pi/pic/*.jpg")
    files.sort()
    #print files

    for f in files:
        #print 'f=%s' % f
        number=getIndex(f)
        print 'AT 1 numStr %d' % number
        clips[number].append(f)
        #print "AT 2 File %s, number %d" % (f,number)

    print "AT 3 Clips.keys = %s" % clips.keys()
    currentClip=clips.keys()[0]
    print "Current Clip %s" % currentClip

    currentIndex=0
    response = Response(open(clips[currentClip][currentIndex],'rb').read())

    templateData = {
      'mySize': mySize,
      'clipName' : getClipName(clips[currentClip][currentIndex],len(clips[currentClip]))
      }
    print "AT 4"
    return render_template('index.html', **templateData)


@app.route('/command', methods=['GET', 'POST'])
def command():
    global guiCmd, mySize, guiCmdOld, currentClip, currentIndex, response, clips

    print "AT 6"
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
    print 'AT 7 guiCmd = %d' % guiCmd

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
            #print "Name %s File %s" % (name,f)
            #newFile='/home/dlacres/pic/+name'
            #print newFile
            shutil.copyfile(f,'/home/dlacres/pic/'+name)
    elif guiCmd==6:#Delete All Pictures
        for key in sorted(clips.keys()):
            files=clips[key]
            for file in files:
                os.remove(file)
        

    guiCmdOld=guiCmd                
    #print 'Clip %s index %s' % (currentClip,currentIndex)
    print clips[currentClip][currentIndex]
    templateData = {
      'mySize': mySize,
      'clipName' : getClipName(clips[currentClip][currentIndex],len(clips[currentClip]))
      }

    #print templateData
    return render_template('index.html', **templateData)

def gen(stringNumber):
    global guiCmd, isPlay, isBack, clips

    if guiCmd==2: #Play
        frames=clips[stringNumber]
    else:         #Backward Play
        frames=reversed(clips[stringNumber])

    for frame in frames:
        time.sleep(.2)
        print 'AT 7 %s' % frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open(frame,'rb').read() + b'\r\n')


@app.route('/picture_feed')
def picture_feed():
    global response

    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

