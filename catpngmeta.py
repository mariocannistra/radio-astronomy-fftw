#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# this program can be launched manually to display radio astronomy
# related metadata eventually present in a png file

from PIL import Image, ImageFont, ImageDraw, PngImagePlugin
import sys

inpname = sys.argv[1]

old_im = Image.open( inpname )
metadict = old_im.info
for key in metadict:
    if key[:3]=='ra-':
        print(key + '\t' + metadict[key])
