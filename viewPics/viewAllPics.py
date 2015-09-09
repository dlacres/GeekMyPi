#!/usr/bin/env python

import pyglet
import argparse
import os

def updateImage(dt):

    try:
      image1 = pyglet.image.load(ip.next())
      sprite.image = image1
      sprite.scale = getScale(window, image1)
    except StopIteration:
      print "***All Done***"
      pyglet.clock.unschedule(updateImage)
      pyglet.app.exit()

    window.clear()

def getImagePaths(input_dir='.'):
    paths = []
    for root, dirs, files in os.walk(input_dir, topdown=True):
        for file in sorted(files):
            if file.endswith(('jpg', 'png', 'gif')):
                path = os.path.abspath(os.path.join(root, file))
                paths.append(path)
    return paths

def getScale(window, image):
    if image.width > image.height:
        scale = float(window.width) / image.width
    else:
        scale = float(window.height) / image.height
    return scale


window = pyglet.window.Window(600, 400)

@window.event
def on_draw():
    sprite.draw()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Dir of Images', 
      nargs='?', 
      default=os.getcwd())
    
    args = parser.parse_args()

    image_paths = getImagePaths(args.dir)
    ip = iter(image_paths)
    try:
      img = pyglet.image.load(ip.next())
      sprite = pyglet.sprite.Sprite(img)
      sprite.scale = getScale(window, img)

      pyglet.clock.schedule_interval(updateImage, .05)

      pyglet.app.run()
    except StopIteration:
      print "** There were no images to show **"
      print "** Usage python viewAllPics.py MyImagePath **"
      print "** Usage cd MyImagePath then python viewAllPics.py **"
