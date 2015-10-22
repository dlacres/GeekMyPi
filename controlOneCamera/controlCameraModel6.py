from Tkinter import *
import ttk
import socket
import os
import threading
import time
import Queue
#import subprocess
import cv2
import urllib
import numpy as np
import PIL.Image
import PIL.ImageTk
import ImageTk
import urllib,urllib2
import base64
import ImageOps
import Image

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


    #stream=urllib.urlopen(urlStream)
    #stream=urllib.urlopen('http://192.168.1.110:8081/?action=stream')
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





