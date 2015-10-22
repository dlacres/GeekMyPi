import socket
import sys
import os
import re
import subprocess
import glob
#from sendfile import sendfile

picturePath = '/home/pi/tmp'
ipAddress = '192.168.1.118' #R pi
#ipAddress = '192.168.1.104' #Dell PC
port = 1234

def process_exists(proc_name):
    ps = subprocess.Popen("ps ax -o pid= -o args= ", shell=True, stdout=subprocess.PIPE)
    ps_pid = ps.pid
    output = ps.stdout.read()
    ps.stdout.close()
    ps.wait()

    for line in output.split("\n"):
        res = re.findall("(\d+) (.*)", line)
        if res:
            pid = int(res[0][0])
            if proc_name in res[0][1] and pid != os.getpid() and pid != ps_pid:
                return True
    return False

def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i+1)*10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

print('Trying to connect...')
s = socket.socket()
#s.connect(('192.168.1.104', 1234))
s.connect((ipAddress, port))

print('Connected. Wating for command.')

i_f=0
f=[]

while True:
    #### RECEIVE A
    cmd = s.recv(32)

    if cmd == 'getpicnamereset':
      f=glob.glob(picturePath+'/*.jpg')
      i_f=0
      if f==[]:
        s.sendall('end')
      else:
        s.sendall(f[i_f])

    elif cmd == 'getcameraname':
      hn = socket.gethostname()
      s.sendall(hn)

    elif cmd == 'getpicname':
      i_f+=1
      if f!=[]:
        if i_f>len(f)-1:
          i_f=-1
          f=[]
          s.sendall('end')
          print(' ... getpicname 1')
        else:
          s.sendall(f[i_f])
          print(' ... getpicname 2 - '+ f[i_f])
      else:
        f=glob.glob(picturePath+'/*.jpg')
        i_f=0
        if f==[]:
          s.sendall('end')
          print(' ... getpicname 3')
        else:
          s.sendall(f[i_f])
          print(' ... getpicname 4')

    elif cmd == 'getcurrentpicname':
      if f==[]:
        i_f=0
        f=glob.glob(picturePath+'/*.jpg')
        if f==[]:
          s.sendall('end')
          print(' ... at 1')
        else:
          s.sendall(f[i_f])
          print(' ... at 2')
      else:
        if (i_f>len(f)-1):
          i_f = len(f)-1
          print(' ... at 3')
        s.sendall(f[i_f])
        print(' ... at 4')
    elif cmd == 'getfilesize':
      if (len(f[i_f])>0):
        blocksize=os.path.getsize(f[i_f])
        s.send(str(blocksize))
        print(' ... blocksize = '+str(blocksize))
      else:
        s.send('end')
        print(' ... no file length')

    elif cmd == 'sendfile':
      # Must call 'getfilesize' before calling this
      if (blocksize>0):
     
        f_hdl=open(f[i_f],"rb")
        f_part=f_hdl.read(1024)
        while (f_part):
          s.send(f_part)
          f_part=f_hdl.read(1024)

        f_hdl.close()
      else:
        print(' ... break')

      print('"sendfile" command complete. ['+f[i_f]+']')

    elif cmd == 'end':
      print('"end" command received. Teminate.')
      s.sendall("End Received")
      break

    elif cmd == 'ping':
      print('"ping" command received')
      s.sendall("ping back")

    elif cmd == 'check':
      print('"check" command received')
      s.sendall("isAlive")

    elif cmd== 'checkmotion':
      if process_exists('motion'):
        print('"check" motion running')
        s.sendall('motion running')
      else:
        print ('"check" motion stopped')
        s.sendall('motion stopped')

    elif cmd=='stopmotion':
      os.system('sudo /etc/init.d/motion stop')
      s.sendall('motion stoped')
      print ('"stopmotion"')

    elif cmd=='startmotion':
      os.system('sudo /etc/init.d/motion start')
      s.sendall('motion started')
      print('"startmotion"')

    elif cmd == 'getdiskspace':
      print('"getDiskSpace" command received')
      st = os.statvfs('/')
      siz=bytes2human(st.f_bavail*st.f_frsize)
      s.sendall(siz)

    elif cmd == 'deletefile':
      print('"deletfile" command received')
      os.remove(f[i_f])
      s.sendall('file deleted')

    elif cmd == 'getfilesize':
      if (len(f[i_f]>0)):
        size=str(os.path.getsize(f[i_f]))
        print('"getfilesize" ['+f[i_f]+"] size ["+size+"]") 
        s.sendall(size)
      else:
        s.sendall('end')

    else:
      print ('Cmd not recognized')
      s.sendall('Cmd not recognized')
