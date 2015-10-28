from Tkinter import *
import ttk, socket, os, threading, time, Queue, cv2, urllib, shutil
import numpy as np
import PIL.Image
import PIL.ImageTk
import ImageTk
import urllib,urllib2
import base64
import ImageOps
import Image
from collections import defaultdict
import glob

#urlStream='http://192.168.1.110:8081/?action=stream'
urlStream='http://192.168.1.115:8081/?action=stream'
fileDir='./Camera1/'
fileSocket=1234
username = "xx"
password = "xxxxx"

#--------------------------------------------------------------------------------
class controlCameraModel:
  def __init__(self,hui):
    self.hui=hui
    print ' ... Waiting for clinet to connect...'
    self.startSocket()
    print ' ... Connected.'

  def startSocket(self):
    self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.c.bind(('', fileSocket))
    #self.c.bind(('', 1234))
    self.c.listen(1)
    self.s, self.a = self.c.accept()

  def deleteFileName(self):
    self.s.sendall('deletefile')
    msg=self.s.recv(1024)
    return(msg)

  def setCameraThread(self, ct):
    self.ct=ct

  def getNextFilePath(self):
    self.s.sendall('getpicname')
    msg=self.s.recv(1024)
    return(msg)

  def checkMotionRunning(self):
    self.s.sendall('checkmotion')
    msg=self.s.recv(1024)
    return(msg)

  def stopMotionRunning(self):
    self.s.sendall('stopmotion')
    msg=self.s.recv(1024)
    return(msg)

  def startMotionRunning(self):
    self.s.sendall('startmotion')
    msg=self.s.recv(1024)
    return(msg)

  def getDiskSpaceLeft(self):
    self.s.sendall('getdiskspace')
    msg=self.s.recv(1024)
    return(msg)

  def getCurrentPicName(self):
    self.s.sendall('getcurrentpicname')
    msg=self.s.recv(1024)
    return(msg)

  def getCameraName(self):
    self.s.sendall('getcameraname')
    msg=self.s.recv(1024)
    return(msg)

  def getFileSize(self):
    self.s.sendall('getfilesize')
    siz_s = self.s.recv(10)
    try:
      siz_i = int(siz_s)
    except ValueError:
      siz_i=-1

    return(siz_i)

  def getFile(self,filePath,siz_i):
    self.s.sendall('sendfile')

    # Strip off the path from the file name
    fileList = filePath.split('/')
    fileName = fileList[len(fileList)-1]

    if (siz_i>0):
      f = open(fileDir+fileName,'wb') #open in binary
      while (True):
        try:
          l = self.s.recv(1024)
        except socket.error, e:
          err - e.args[0]
          if err==errno.EAGAIN or err == errno.EWOULDBLOCK:
            print('No data available')
          else:
            print e
            sys.exit(1)
        
        try:
          siz_i-=len(l)
        except:
          break

        f.write(l)
        if (siz_i<=0):
          break
      f.close()
    else:
      print('... break')
  

    #print(' ... "sendfile" command complete ['+fileName+']')

    # Compare file sizes
    sizLocal_i=os.path.getsize(fileDir+fileName)
    #### SEND
    self.s.sendall('getfilesize')
    sizClient_s=''
    #### Receive
    sizClient_s=self.s.recv(10)

    return(sizLocal_i-int(sizClient_s))

#--------------------------------------------------------------------------------
class controlCameraThread:
  def __init__(self, hui, cc):
    self.hui=hui
    self.cc = cc
    self.commQueue = Queue.Queue()
    self.hui.root.bind('<<whenClientChanged>>', self.clientChanged)
    self.th=threading.Thread(target=self.checkClientThread)
    self.th.daemon = True
    self.startThread()
    self.th.start()

  def stopThread(self):
    self.runThread=False

  def startThread(self):
    self.runThread=True

  ## Function run in thread
  def checkClientThread(self):
    num=0

    while(True):
      if (self.runThread):
        ## Each time the time increases, put the new value in the queue...
        self.commQueue.put(self.cc.checkMotionRunning())
        self.commQueue.put(self.cc.getDiskSpaceLeft())
        self.commQueue.put(self.cc.getCameraName())
        #self.commQueue.put(self.cc.getCurrentPicName())
  
        ## ... and generate a custom event on the main window
        try:
          self.hui.root.event_generate('<<whenClientChanged>>', when='tail')
        ## If it failed, the window has been destoyed: over
        except TclError:
          print('TCL Error')
          break

# Get Files ----------------------
        # Get the next file name
        filePath=self.cc.getNextFilePath()
        print('File Path = ['+filePath+']')

        # Get the size of the file
        if (len(filePath)>0 and filePath!='end'):
          siz = self.cc.getFileSize()

          print('... filesize is '+str(siz))

          # Check that a file exists. Break if it does not
          if (siz > 0):

            # Get the file
            size=self.cc.getFile(filePath, siz)

            print('... getfile diff is '+str(size))

            # Check that the file saved is the same size as the file sent
            if (size==0):
              # If the file was received OK, Delete the file
              self.cc.deleteFileName()
            else:
              print(' . ERROR File Size Different for '+filePath)
          else:
            self.cc.deleteFileName()

        print('end of loop ['+str(num)+']')
        num+=1
      ## Next
      time.sleep(1)

  ## Use a binding on the custom event to get the new time value
  ## and change the variable to update the display
  def clientChanged(self,event):
    self.hui.isAlive.set(self.commQueue.get())
    self.hui.diskSpace.set(self.commQueue.get())
    self.hui.cameraName.set(self.commQueue.get())
    #self.hui.fileName.set(self.commQueue.get())

#--------------------------------------------------------------------------------
class streamVideoThread:
  def __init__(self,hui):
    self.hui=hui
    self.commQueue = Queue.Queue()
    self.hui.root.bind('<<whenClientChanged2>>', self.clientChanged)
    self.th=threading.Thread(target=self.streamVideo)
    self.th.daemon = True
    self.startThread()
    self.th.start()
 
  def stopThread(self):
    self.runThread=False

  def startThread(self):
    self.runThread=True

  ## Function run in thread
  def streamVideo(self):

    req = urllib2.Request(urlStream)
    try:
      stream = urllib2.urlopen(req)
    except IOError, e:
      base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
      req.add_header("Authorization", "Basic %s" % base64string)
      try:
        stream = urllib2.urlopen(req)
      except IOError, e:
        pass
      else:
        print "This page is not protected by authentication."
        #sys.exit(1)
      pass
    else:
      # If we don't fail then the page isn't protected
      print "This page isn't protected by authentication."

    print 'url opened '+str(self.runThread)
    bytes=''
    while(self.runThread):
      bytes+=stream.read(1024)
      a=bytes.find('\xff\xd8')
      b=bytes.find('\xff\xd9')
      if (a!=-1 and b!=-1):
        #print len(bytes)
        jpg = bytes[a:b+2]
        self.commQueue.put(jpg)
        bytes=bytes[b+2:]

        try:
          self.hui.root.event_generate('<<whenClientChanged2>>', when='tail')
        ## If it failed, the window has been destoyed: over
        except TclError:
          print " ... ERROR TclError in Video Stream"
          break

  ## Use a binding on the custom event to get the new time value
  ## and change the variable to update the display
  def clientChanged(self,event):
    #print "   ... video Client Changed"
    jpg=self.commQueue.get()
    cv_image=cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    pil_image = PIL.Image.fromarray(cv_image)
    pil_image2 = ImageOps.fit(pil_image, (640,360), Image.ANTIALIAS)
    tk_image = ImageTk.PhotoImage(image=pil_image2)

    self.hui.image_label.configure(image=tk_image)
    self.hui.image_label._image_cache = tk_image  # avoid garbage collection
    self.hui.root.update()

# Motion %Cam(2)_Clip(2-4)-%Y(4)%m(2)%d(2)%H(2)%M(2)%S(2)-Seq(2)

# cam clip year month day hour min sec seq
# 1   2    3    4     5   6    7   8   9
# 0   1    2    3     4   5    6   7   8

class findImageFiles:
  def __init__(self,hui):
    self.imagePath = "./small/*.jpg"
    self.hui=hui
    self.currentIndex=0
    self.clips = defaultdict(list)
    self.currentClip=0
    self.findImageInADay()

  def splitString(self,s):
    strLen=0
    strIdx=0
    aStr=''
    listStr=['']
    s2=''


    # strip off the path
    inName=False
    for c in s:
      if c=='/':
        s2=''
        inName=True
      else:
        s2=s2+c
      if c=='.' and inName:
        break

    #print '... AT 1.5 s2 = ['+s2+']'    

    for c in s2:
      #print 'AT 6 ['+c+']'

      if (c=='_' or c=='-'):
        listStr.append(aStr)
        #print 'AT a ['+str(strIdx)+']['+aStr+']['+c+']'
        aStr=''
        strIdx+=1
        strLen=-1
      elif c=='-':
        listStr.append(aStr)
        #print 'AT b ['+str(strIdx)+']['+aStr+']['+c+']'
        aStr=''
        strIdx+=1
        strLen=-1
      elif strIdx==2 and strLen==3:
        aStr=aStr+c
        listStr.append(aStr)
        #print 'AT c ['+str(strIdx)+']['+aStr+']['+c+']'
        aStr=''
        strIdx+=1
        strLen=-1
      elif strLen==1 and not (strIdx==0 or strIdx==1 or strIdx==2 or strIdx==7):
        aStr=aStr+c
        listStr.append(aStr)
        #print 'AT d ['+str(strIdx)+']['+aStr+']['+c+']'
        aStr=''
        strIdx+=1
        strLen=-1
      else:
        aStr=aStr+c
        #print 'AT e ['+str(strIdx)+']['+c+']'

      strLen+=1

    #print 'AT 5 ['+aStr+']'

    return listStr

  def getIndex(self,s):
    num=0

    l=self.splitString(s)

    #print 'AT 1 len ['+str(len(l))+']'

    #      cam  mon  day
    numStr=l[1]+l[4]+l[5]
    try:
        num=int(numStr)
    except ValueError:
        print 'ERROR 1'
    return num

  def findImageInADay(self):

    #print '... AT 1.3'
    files=glob.glob(self.imagePath)
    #print '... AT 1.4'
    files.sort()
    #print '... AT 1.5'

    #print '... Found '+str(len(files))+' files at location '+self.imagePath

    for f in files:
      #print '... f=%s' % f
      number=self.getIndex(f)
      #print '... AT 1.1 numStr %d' % number
      self.clips[number].append(f)
      #print "... AT 2 File %s, number %d" % (f,number)

    #print "AT 3 Clips.keys = %s" % clips.keys()
    #currentClip=clips.keys()[0]
    #print "Current Clip %s" % currentClip

  def getNextDay(self):
    self.currentClip=next((key for key in sorted(self.clips.keys()) if key > self.currentClip),self.currentClip)

  def getNextClip(self):
    if self.currentIndex==0:
      self.currentClip=self.clips.keys()[0]
    self.currentIndex+=1
    if self.currentIndex>=len(self.clips[self.currentClip]):
      r=''
      self.currentIndex=0
    else:
      r=self.clips[self.currentClip][self.currentIndex]
    #currentClip=next((key for key in sorted(clips.keys()) if key > currentClip),currentClip)
    return(r)

  def showPicture(self):

    while True:
      f=self.getNextClip()
      if f:
        jpg2=Image.open(f)
        #jpg2 = jpg.resize((640,360),Image.ANTIALIAS)
        tk_image = ImageTk.PhotoImage(image=jpg2)
        self.hui.image_label.configure(image=tk_image)
        self.hui.image_label._image_cache = tk_image  # avoid garbage collection
        self.hui.root.update()
      else:
        break

    #print f
    #jpg = cv2.imread(f)
    #jpg2 = cv2.resize(jpg,None,fx=.5,fy=.5,interpolation=cv2.INTER_AREA)
    
    #cv_image=cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
    #cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    #pil_image = PIL.Image.fromarray(cv_image)
    #pil_image2 = ImageOps.fit(pil_image, (640,360), Image.ANTIALIAS)
     
class showImages:

  def __init__(self,hui):
    self.imagePath = "/home/pi/Camera1/small/*.jpg"
    self.hui=hui

  def getAllFileNames(self):
    self.files=glob.glob(self.imagePath)
    self.files.sort()

  def showImages(self):
    print '... At 0'
    for f in self.files:
      print '... At 1 '+f
      jpg=Image.open(f)
      tk_image = ImageTk.PhotoImage(image=jpg)
      self.hui.image_label.configure(image=tk_image)
      self.hui.image_label._image_cache = tk_image  # avoid garbage collection
      self.hui.root.update()
   




