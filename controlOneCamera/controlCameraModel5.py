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

class controlCameraModel:
  def __init__(self,hui):
    self.hui=hui
    print ' ... Waiting for clinet to connect...'
    self.startSocket()
    print ' ... Connected.'

  def startSocket(self):
    self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.c.bind(('', 1234))
    self.c.listen(1)
    self.s, self.a = self.c.accept()

  def deleteFileName(self):
    self.s.sendall('deletefile')
    msg=self.s.recv(1024)
    return(msg)

  def setCameraThread(self, ct):
    self.ct=ct

  def startLiveStream(self):

    self.lst=streamVideoThread(self.hui)
    print 'Start Live View'

    return

  def stopLiveStream(self):

    self.lst.stopThread()
    print 'stop live view'

    #self.ct.stopThread()
    #self.ct.startThread()
    return

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

  def getFile(self,filePath):

    #### SEND A
    self.s.sendall('sendfile')

    # Strip off the path from the file name
    fileList = filePath.split('/')
    fileName = fileList[len(fileList)-1]

    print(' ... Filename = '+fileName)

    f = open('./'+fileName,'wb') #open in binary
    siz_s = ''
    try:

      #### RECEIVE B
      siz_s = self.s.recv(10)
    except socket.error, e:
      err - e.args[0]
      if err==errno.EAGAIN or err == errno.EWOULDBLOCK:
        print('No data available')
      else:
        print e
        sys.exit(1)

    print (' ... Size = ' + siz_s)
    siz_i=int(siz_s)

    while (True):
      #### RECEIVE C
      l = self.s.recv(1024)
      siz_i-=len(l)
      #print(' ... size of = '+str(siz_i))
      f.write(l)
      if (siz_i<=0):
        break

    f.close()

    print(' ... Filename Received')

    # Compare file sizes
    sizLocal_i=os.path.getsize('./'+fileName)
    #### SEND
    self.s.sendall('getfilesize')
    sizClient_s=''
    #### Receive
    sizClient_s=self.s.recv(10)

    return(sizLocal_i-int(sizClient_s))

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

    while(True):
      if (self.runThread):
        ## Each time the time increases, put the new value in the queue...
        self.commQueue.put(self.cc.checkMotionRunning())
        self.commQueue.put(self.cc.getDiskSpaceLeft())
        self.commQueue.put(self.cc.getCameraName())
        self.commQueue.put(self.cc.getCurrentPicName())

        ## ... and generate a custom event on the main window
        try:
          self.hui.root.event_generate('<<whenClientChanged>>', when='tail')
        ## If it failed, the window has been destoyed: over
        except TclError:
          break
      
      ## Next
      time.sleep(1)

  ## Use a binding on the custom event to get the new time value
  ## and change the variable to update the display
  def clientChanged(self,event):
    self.hui.isAlive.set(self.commQueue.get())
    self.hui.diskSpace.set(self.commQueue.get())
    self.hui.cameraName.set(self.commQueue.get())
    self.hui.fileName.set(self.commQueue.get())


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
    stream=urllib.urlopen('http://192.168.1.110:8081/?action=stream')
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
    tk_image = ImageTk.PhotoImage(image=pil_image)

    self.hui.image_label.configure(image=tk_image)
    self.hui.image_label._image_cache = tk_image  # avoid garbage collection
    self.hui.root.update()





