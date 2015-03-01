from time import time
import glob

class Camera(object):
    """An emulated camera implementation that streams a repeated sequence of
    files 1.jpg, 2.jpg and 3.jpg at a rate of one frame per second."""

    def __init__(self, filter):
        self.files = glob.glob("/home/pi/camera1/"+filter)
        #self.files = glob.glob("/media/networkshare/CameraEntry/*.jpg")
        #self.files=glob.glob("/tmp/*.jpg")
        self.files.sort()
        self.frames = [open(f, 'rb').read() for f in self.files]
        self.idx=0

    def get_pics(self, filter):
        self.files = glob.glob("/home/pi/camera1/"+filter)
        self.files.sort()
        self.frames = [open(f,'rb').read() for f in self.files]
        self.idx=0

    def reset_frame(self):
        self.idx=0

    def get_frame(self):
        if self.idx<len(self.frames)-1:
            self.idx=self.idx+1
        return self.frames[self.idx]

