from Tkinter import *
import ttk
import socket
import os

class clientConnect:
  def connect(self):

    print ' ... Waiting for clinet to connect...'
    self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.c.bind(('', 1234))
    self.c.listen(1)
    self.s, self.a = self.c.accept()

    print ' ... Connected.'

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

    ttk.Button(self.mainframe, text="End", command=endButton).grid(column=1, row=4, sticky=W)
    ttk.Button(self.mainframe, text="Get Files", command=getFilesButton).grid(column=2, row=4, sticky=W)
    ttk.Button(self.mainframe, text="sendCmd", command=sendCmdButton).grid(column=3, row=4, sticky=W)

    ttk.Label(self.mainframe, textvariable=self.isAlive).grid(column=3, row=1, sticky=(W, E))
    self.isAlive.set("notAlive")
    ttk.Label(self.mainframe, text="Camera Name").grid(column=1, row=1, sticky=W)
    ttk.Label(self.mainframe, textvariable=self.cameraName).grid(column=2, row=1, sticky=(W, E))
    self.cameraName.set("None")

    ttk.Label(self.mainframe, text="Disk Space").grid(column=1, row=2, sticky=W)
    ttk.Label(self.mainframe, textvariable=self.diskSpace).grid(column=2, row=2, sticky=(W, E))
    self.diskSpace.set("None")

    ttk.Label(self.mainframe, text="File Name").grid(column=1, row=3, sticky=W)
    ttk.Label(self.mainframe, textvariable=self.fileName).grid(column=2, row=3, sticky=(W, E))
    self.fileName.set("None")
    ttk.Label(self.mainframe, textvariable=self.filesReceived).grid(column=3, row=3, sticky=(W, E))
    self.filesReceived.set("0 of 0")

    ttk.Label(self.mainframe, text="Command").grid(column=1, row=5, sticky=W)
    ttk.Entry(self.mainframe, textvariable=self.cmdSent).grid(column=2, row=5, sticky=(W, E))
    self.root.bind("<Return>", sendCmdButton)
    self.cmdSent.set("getpicname")

    ttk.Label(self.mainframe, text="Message").grid(column=1, row=6, sticky=W)
    ttk.Label(self.mainframe, textvariable=self.msgReceived).grid(column=2, row=6, sticky=(W, E))
    self.msgReceived.set("no message")
    for child in self.mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

def endButton(*args):
  cc.s.sendall('end')
  hui.root.quit()
  return

def getFilesButton(*args):

  while(True):

    # Get the next file name
    filePath=getNextFilePath():

    # Check that a file exists. Break if it does not
    if (len(filePath)<2):
      print(' ... Done getting files')
      break

    # Get the file
    getFile(filePath)

    # Check that the file saved is the same size as the file sent
    if (fileSizeIsSame()):
      # If the file was received OK, Delete the file
      deleteFileName()
    else:
      print(' . ERROR File Size Different for '+filePath)

  return

def fileSizeIsSame():
  return(True)

def deleteFileName():
  cc.s.sendall('deletefile')
  msg=cc.s.recv(1024)
  hui.msgReceived.set(msg)
  return

def getNextFilePath():
  cc.s.sendall('getpicname')
  msg=cc.s.recv(1024)
  hui.msgReceived.set(msg)
  return(msg)

def getFile(filePath):

  cc.s.sendall('sendfile')

  # Strip off the path from the file name
  fileList = filePath.split('/')
  fileName = fileList[len(fileList)-1]

  print(' ... Filename = '+fileName)

  f = open('./'+fileName,'wb') #open in binary
  siz_s = cc.s.recv(10)

  print (' ... Size = ' + siz_s)
  siz_i=int(siz_s)

  l = cc.s.recv(1024)
  while (True):
    siz_i-=len(l)
    print(' ... size of = '+str(siz_i))
    f.write(l)
    if (siz_i<=0):
      break
    l = cc.s.recv(1024)
  f.close()

  print(' ... Filename Received')

  # Compare file sizes
  sizLocal_i=os.path.getsize('./'+

  hui.msgReceived.set('Received File '+fileName)
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


# Launch the server and UI
cc=clientConnect()
cc.connect()

hui=healthUi()
hui.root.mainloop()



