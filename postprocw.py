#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# this program is launched with proper parameters by  doscanw.py  OR  reprocessw.py
# will produce the spectrograms, upload to AWS S3 if enabled, send mqtt notifications if enabled

# BEFORE RUNNING A SESSION SCAN (with bash runw.sh) please set your configuration values in file  radioConfig.py

import paho.mqtt.client as paho
import socket
import ssl
from boto.s3.key import Key
import boto.s3.connection
import csv
import sys
import numpy as np
import os
import subprocess
import time
import radioConfig
from time import sleep
from PIL import Image, ImageFont, ImageDraw, PngImagePlugin
import copy
import pytz
import calendar
from datetime import datetime, timedelta
import ntpath

def outmsg(smsg):
    thisprogmsg = "..postprocw.py: " + smsg
    print(thisprogmsg)

def push_picture_to_s3(id):
	# id should have the folder name as YYYYMMDD/filename.ext

    BUCKET_NAME = 'jupiter-spectrograms'
    AWS_ACCESS_KEY_ID = radioConfig.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = radioConfig.AWS_SECRET_ACCESS_KEY

    # connect to the bucket
    conn = boto.s3.connect_to_region('eu-central-1',
       aws_access_key_id=AWS_ACCESS_KEY_ID,
       aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
       is_secure=True,               # uncommmnt if you are not using ssl
       calling_format = boto.s3.connection.OrdinaryCallingFormat(),
       )

    #print(conn)

    keyname = '%s/%s' % ( radioConfig.scanTarget, id )
    #print(keyname)

    #fn = '%s.png' % id
    fn = id
    #print(fn)

    bucket = conn.get_bucket(BUCKET_NAME)
    #print(bucket)

    #print "uploading file"
    key = bucket.new_key(keyname)
    key.set_contents_from_filename(fn)
    outmsg('file uploaded to aws s3')

    outmsg("setting acl to public read")
    key.set_acl('public-read')

    # we need to make it public so it can be accessed publicly
    # using a URL like http://s3.amazonaws.com/bucket_name/key
    outmsg("making key public")
    key.make_public()

connflag = False

def on_connect(client, userdata, flags, rc):
    global connflag
    connflag = True
    outmsg("mqtt connection returned result: " + str(rc))

def on_message(client, userdata, msg):
    outmsg(msg.topic+" "+str(msg.payload))

#def on_log(client, userdata, level, buf):
#    outmsg msg.topic+" "+str(msg.payload)

mqttc = paho.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
#mqttc.on_log = on_log

awshost = "data.iot.eu-west-1.amazonaws.com"
awsport = 8883
clientId = "mcawsthings-test2"
thingName = "mcawsthings-test2"
caPath = "./aws-iot-rootCA.crt"
certPath = "./cert.pem"
keyPath = "./privkey.pem"

if radioConfig.sendIoTmsg:
	mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
	mqttc.connect(awshost, awsport, keepalive=5)
	mqttc.loop_start()

off2sub = radioConfig.upconvFreqHz

sessionfolder = sys.argv[4]
metaname = sessionfolder + os.sep + sys.argv[1] + ".met"

fileDate = sys.argv[1][3:11]

msg = "fileDate: " + fileDate
outmsg(msg)

globmin = float(sys.argv[2])
globmax = float(sys.argv[3])
#these will be <> 0 only when post processing at end of session:
if globmin==0.0 and globmax==0.0:
	rangespec = False
else:
	rangespec = True

if len(sys.argv) == 6:
    selcmap = sys.argv[5]
else:
    selcmap = "RdYlBu"	# PiYG PRGn BrBG PuOr RdGy RdBu RdYlBu RdYlGn Spectral coolwarm bwr seismic


def diffdates(d1, d2):
    #Date format: %Y-%m-%d %H:%M:%S
    return (time.mktime(time.strptime(d2,"%Y-%m-%d %H:%M:%S")) -
               time.mktime(time.strptime(d1, "%Y-%m-%d %H:%M:%S")))

with open(metaname, 'r') as f:
    linein = f.readline()
    inflds = linein.split()
    bincols = inflds[0]
    linein = f.readline()
    inflds = linein.split()
    binrows = inflds[0]
    linein = f.readline()
    inflds = linein.split()
    startFreq = int(inflds[0])
    linein = f.readline()
    inflds = linein.split()
    endFreq = int(inflds[0])
    linein = f.readline()
    inflds = linein.split()
    stepFreq = int(inflds[0])
    linein = f.readline()
    inflds = linein.split()
    effIntTime = float(inflds[0])
    linein = f.readline()
    inflds = linein.split()
    avgScanDur = float(inflds[0])
    linein = f.readline()
    inflds = linein.split()
    firstAcqTimestamp = inflds[0] + ' ' + inflds[1]
    linein = f.readline()
    inflds = linein.split()
    lastAcqTimestamp = inflds[0] + ' ' + inflds[1]

    linein = f.readline()
    inflds = linein.split()
    samplingRate = inflds[0]
    linein = f.readline()
    inflds = linein.split()
    hops = inflds[0]
    linein = f.readline()
    inflds = linein.split()
    cropPercentage = inflds[0]
    linein = f.readline()
    inflds = linein.split()
    cropExcludedBins = inflds[0]
    linein = f.readline()
    inflds = linein.split()
    cropFreqOffset = inflds[0]

matorg = '(' + bincols + ',' + binrows + ')'

startFreq = startFreq - radioConfig.upconvFreqHz
endFreq = endFreq - radioConfig.upconvFreqHz

cropRelatedReduction = ( int(cropExcludedBins) / 2 ) * stepFreq

startFreq = startFreq + cropRelatedReduction
endFreq = endFreq - cropRelatedReduction

#cmdstring = "gnuplot -e \"scanstart='%s'\" -e \"scanend='%s'\" -e fstart=%d -e fend=%d -e fstep=%d -e singlescandur=%f -e \"matorg='%s'\" -e \"outname='%s'\" -e globmin=%f -e globmax=%f plotmin.gnu" % (firstAcqTimestamp, lastAcqTimestamp, startFreq, endFreq, stepFreq, avgScanDur, matorg, sys.argv[1], globmin, globmax)

cmdstring = "python pyrend.py %s %f %f %s %s" % ( sys.argv[1], globmin, globmax, sys.argv[4], selcmap )

outmsg(cmdstring)

outmsg("generating heatmap")
p = subprocess.Popen(cmdstring, shell = True)
outmsg("started pyrend.py")
# comment out the following to avoid waiting for pyrend:
#os.waitpid(p.pid, 0)
p.wait()
if p.returncode != 0:
	print('Error running pyrend.py\n')
	print('postprocw.py interrupted')
	sys.exit(10)
else:
	outmsg("pyrend completed")

outname = sessionfolder + os.sep + sys.argv[1]
thumbname =  sessionfolder + os.sep + sys.argv[1] + '.gif'

# load image and get size info
old_im = Image.open(outname + '.png')
old_size = old_im.size
ow, oh = old_im.size

if radioConfig.generateThumbs == True:
	outmsg("generating thumbnail")
	# create thumbnail in gif format
	thumb = copy.deepcopy(old_im)
	thumb.thumbnail( (ow/10,oh/10) , Image.ANTIALIAS)
	thumb.save(thumbname,'GIF')

outmsg("performing palette conversion")
# this is necessary to keep image file size at a minimum
# ( it's also the file mode used by gnuplot )
new_im = old_im.convert('P', palette=Image.ADAPTIVE, colors=256)

outmsg("adding metadata to image")
# create and attach info dictionary with metadata
meta = PngImagePlugin.PngInfo()
meta.add_text("ra-stationID", radioConfig.stationID)
meta.add_text("ra-scanTarget", radioConfig.scanTarget)
meta.add_text("ra-FFTbins", str(bincols))
meta.add_text("ra-scans", str(binrows))
meta.add_text("ra-FreqStart", str(startFreq))
meta.add_text("ra-FreqEnd", str(endFreq))
meta.add_text("ra-FreqStep", str(stepFreq))
meta.add_text("ra-effIntTime", str(effIntTime))
meta.add_text("ra-avgScanDur", str(avgScanDur))
meta.add_text("ra-scanTimestampFirst", firstAcqTimestamp)
meta.add_text("ra-scanTimestampLast", lastAcqTimestamp)
meta.add_text("ra-samplingRate", samplingRate)
meta.add_text("ra-upconverterFreq", str(radioConfig.upconvFreqHz))
meta.add_text("ra-hops", hops)
meta.add_text("ra-cropPercentage", cropPercentage)
meta.add_text("ra-cropExcludedBins", cropExcludedBins)
meta.add_text("ra-cropFreqOffset", cropFreqOffset)

# TO DO:  add min and max power level for this image in the meta
# on linux, if you have imagemagick, use this command to view PNG metadata:
#   identify -verbose foo.png

new_im.save(outname + '-annotated.png', "png", pnginfo=meta, optimize=True)

os.remove(outname + '.png')
os.rename(outname + '-annotated.png', outname + '.png')
outmsg("annotated plot saved")

# upload spectrogram file to aws S3
if radioConfig.uploadToS3:
    push_picture_to_s3( fileDate + "/" + sys.argv[1] + ".png" )

if radioConfig.sendIoTmsg:
    # send MQTT notification message
    mqttc.publish("radioscans/" + radioConfig.scanTarget + "/" + fileDate + "/", sys.argv[1]+".png", qos=1)
    outmsg("mqtt notification sent")
    sleep(0.5)
    mqttc.disconnect()
