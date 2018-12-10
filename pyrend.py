#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# this program is launched with proper parameters by  postprocw.py
# will plot a spectrogram, add axes and annotations, using a specified colormap if any

# BEFORE RUNNING A SESSION SCAN (with bash runw.sh) please set your configuration values in file  radioConfig.py

from PIL import Image, ImageDraw
import numpy as np
import matplotlib as mpl

# Force matplotlib to not use any Xwindows backend.
mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
import copy
import time
from datetime import datetime, timedelta
import calendar
import pytz

import matplotlib.dates as mdates
import specview

import radioConfig

def to_datetime_from_utc(time_tuple):
    return datetime.fromtimestamp(calendar.timegm(time_tuple), tz=pytz.utc)

def outmsg(smsg):
    thisprogmsg = "....pyrend.py: " + smsg
    print(thisprogmsg)

ow = 3000
oh = ow / 4 * 3

vmin = float(sys.argv[2])
vmax = float(sys.argv[3])
#these will be <> 0 only when post processing at end of session:
if vmin==0.0 and vmax==0.0:
	rangespec = False
else:
	rangespec = True

sessionfolder = sys.argv[4]

if len(sys.argv) == 6:
    cmapname = sys.argv[5]
else:
    cmapname = "RdYlBu"	# PiYG PRGn BrBG PuOr RdGy RdBu RdYlBu RdYlGn Spectral coolwarm bwr seismic

metaname = sessionfolder + os.sep + sys.argv[1] + '.met'
binname = sessionfolder + os.sep + sys.argv[1] + '.bin'
outname = sessionfolder + os.sep + sys.argv[1] + '.png'

outmsg("reading metadata")
with open(metaname, 'r') as f:
    linein = f.readline()
    inflds = linein.split()
    metaCols = int(inflds[0])
    linein = f.readline()
    inflds = linein.split()
    metaRows = int(inflds[0])
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

dbms = np.fromfile( binname, dtype=np.float32 )

if rangespec == False:
    vmin=dbms.min()
    vmax=dbms.max()
    rangespec = True

msg = "Successfully read %d binary values" % (len(dbms))
outmsg(msg)

dbms = dbms.reshape(metaRows, metaCols)

# rotate to match the way matplotlib works
dbms = np.rot90(dbms,1)
dbms = np.flipud(dbms)

startFreq = startFreq - radioConfig.upconvFreqHz
endFreq = endFreq - radioConfig.upconvFreqHz

cropRelatedReduction = ( int(cropExcludedBins) / 2 ) * stepFreq

startFreq = startFreq + cropRelatedReduction
endFreq = endFreq - cropRelatedReduction

iniTime = to_datetime_from_utc(time.strptime(firstAcqTimestamp, "%Y-%m-%d %H:%M:%S"))
endTime = to_datetime_from_utc(time.strptime(lastAcqTimestamp, "%Y-%m-%d %H:%M:%S"))
inix, endx = mdates.date2num((iniTime, endTime))

fRange = (startFreq, endFreq)

theExtent = [ inix, endx, startFreq, endFreq ]

fig,ax = plt.subplots(figsize=(11.69,8.27), dpi=100)
imgax = specview.RFshow(dbms, ax, cmap=cmapname, cmap_norm='equalize', hs=False, colorbar=True, cb_ticks='stats', nSigma=2, extent=theExtent, origin='lower', aspect='auto', fRange=fRange, FFTbins=metaCols )

plt.title(sys.argv[1], fontsize = 10)

plt.tight_layout()

#plt.show()
fig.savefig(outname, dpi=300)

outmsg("spectrum saved")
