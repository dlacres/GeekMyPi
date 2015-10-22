'''
Created by David Lempia on Sept 11 2015
The MIT License (MIT)

To use, do the following:
1) Run this program
2) Run controlCameraClient6.py on the Raspberry pi camera.

Depends upon:
  controlCameraModel6.py
'''
from Tkinter import *
import ttk
import socket
import os
from controlCameraModel6 import *
from PIL import Image, ImageTk
import cv2
import numpy as np

class healthUi:
  def __init__(self):
    self.root = Tk()
    self.root.title("Control One Camera")

    self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")
    self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    self.mainframe.columnconfigure(0, weight=1)
    self.mainframe.rowconfigure(0, weight=1)

    self.cameraName = StringVar()
    self.diskSpace = StringVar()
    self.fileName = StringVar()
    self.isAlive = StringVar()
    self.filesReceived = StringVar()
    self.cmdSent = StringVar()
    self.msgReceived = StringVar()

    ttk.Button(self.mainframe, text="Exit", command=endButton).grid(column=0, row=0, sticky=W)
    ttk.Button(self.mainframe, text="sendCmd", command=sendCmdButton).grid(column=1, row=0, sticky=W)
    ttk.Entry(self.mainframe, textvariable=self.cmdSent).grid(column=2, row=0, sticky=(W, E))
    self.root.bind("<Return>", sendCmdButton)
    self.cmdSent.set("getpicname")
    ttk.Label(self.mainframe, textvariable=self.msgReceived).grid(column=3, row=0, sticky=(W, E))
    self.msgReceived.set("no message")

    ttk.Label(self.mainframe, text="Camera Name").grid(column=0,row=1, sticky=W)
    ttk.Label(self.mainframe, textvariable=self.cameraName).grid(column=1,row=1, sticky=(W, E))
    self.cameraName.set("None")

    ttk.Label(self.mainframe, text="Is Alive").grid(column=0,row=2, sticky=W)
    ttk.Label(self.mainframe, textvariable=self.isAlive).grid(column=1,row=2, sticky=(W, E))
    self.isAlive.set("notAlive")

    ttk.Label(self.mainframe, text="Disk Space").grid(column=0, row=3, sticky=W)
    ttk.Label(self.mainframe, textvariable=self.diskSpace).grid(column=1, row=3, sticky=(W, E))
    self.diskSpace.set("None")

    self.image_label = ttk.Label(master=self.root)
    self.image_label.grid(column=0, row=1, columnspan=3)

def endButton(*args):
  cc.s.sendall('end')
  hui.root.quit()
  return

def liveViewButton(*args):
  cc.startLiveStream()
  return

def stopLiveViewButton(*args):
  cc.stopLiveStream()
  return

def getFilesButton(*args):

  while(True):

    # Get the next file name
    filePath=cc.getNextFilePath()

    # Check that a file exists. Break if it does not
    if (filePath=='end'):
      print(' ... Done getting files')
      break

    # Get the file
    size=cc.getFile(filePath)

    # Check that the file saved is the same size as the file sent
    if (size==0):
      # If the file was received OK, Delete the file
      cc.deleteFileName()
    else:
      print(' . ERROR File Size Different for '+filePath)

  return

def sendCmdButton(*args):
  global msg

  cmd=hui.cmdSent.get()
  #Protect against a sendfile command. Needs special code to run
  if cmd=='sendfile':
    hui.msgReceived.set('Use the button for this command')
  else:
    cc.s.sendall(cmd)
    msg=cc.s.recv(1024)
    hui.msgReceived.set(msg)
  return

	
# Launch the the control camera model server and UI
hui=healthUi()
cc=controlCameraModel(hui)
ct=controlCameraThread(hui,cc)
st=streamVideoThread(hui)

hui.root.mainloop()



