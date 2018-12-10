#! /usr/bin/env python

import radioConfig
from PIL import Image, ImageFont, ImageDraw, PngImagePlugin
import numpy as np
import matplotlib as mpl
# Force matplotlib to not use any Xwindows backend.
mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
import copy
from glob import glob
import pytz
import time
import calendar
from datetime import datetime, timedelta
import ntpath

import matplotlib.dates as mdates
import specview

def to_datetime_from_utc(time_tuple):
    return datetime.fromtimestamp(calendar.timegm(time_tuple), tz=pytz.utc)

maxcols = 32768

def strinsert(source_str, insert_str, pos):
    return source_str[:pos]+insert_str+source_str[pos:]

sessionfolder = sys.argv[1]
binpattern = sessionfolder + os.sep + "*.bin"

if len(sys.argv) == 3:
    cmapname = sys.argv[2]
else:
    cmapname = "RdYlBu"	# PiYG PRGn BrBG PuOr RdGy RdBu RdYlBu RdYlGn Spectral coolwarm bwr seismic

globmax = -9000
globmin = 9000
gotfirsttime = False

sessmin = np.empty(shape=[0, 1])
sessmax = np.empty(shape=[0, 1])
scantimeline = np.empty(shape=[0, 1])

files_in_dir = sorted(glob(binpattern))
for fname in files_in_dir:
    dbs = np.fromfile(fname, dtype='float32')
    thismin=dbs.min()
    thismax=dbs.max()
    scantime=str(fname)[20:26]
    scandate=str(fname)[12:20]
    print(scandate,scantime,thismin,thismax)
    if thismin < globmin:
        globmin = thismin
    if thismax > globmax:
        globmax = thismax
    sessmin = np.append(sessmin, thismin)
    sessmax = np.append(sessmax, thismax)
    scantime = strinsert(scantime, ":", 2)
    scantime = strinsert(scantime, ":", 5)
    scantimeline = np.append(scantimeline, scantime)

    scanname = fname[:-4]
    metaname = scanname + '.met'
    with open(metaname, 'r') as f:
        linein = f.readline()
        inflds = linein.split()
        metaCols = int( inflds[0] )
        linein = f.readline()
        inflds = linein.split()
        metaRows = int( inflds[0] )
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
        if gotfirsttime == False:
            gotfirsttime = True
            absfirstAcqTimestamp = firstAcqTimestamp
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

overalldbs = np.empty(shape=[metaCols, 0])        
#print "overalldbs.shape: " + str(overalldbs.shape)

mytitle = 'This session signal range: min %.2f .. max %.2f' % (globmin,globmax)
print(mytitle)

files_in_dir = sorted(glob(binpattern))
howmany = len(files_in_dir)
cntfil = 0
for fname in files_in_dir:
    cntfil = cntfil + 1
    scanname = fname[:-4]
    metaname = scanname + '.met'
    with open(metaname, 'r') as f:
        linein = f.readline()
        inflds = linein.split()
        metaCols = int( inflds[0] )
        linein = f.readline()
        inflds = linein.split()
        metaRows = int( inflds[0] )
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

    dbms = np.fromfile( fname, dtype=np.float32 )
    dbms = dbms.reshape(metaRows, metaCols)
    # rotate to match the way matplotlib works
    dbms = np.rot90(dbms,1)
	# reduce the number of samples deleting 1 every 3)
    dbms = np.delete(dbms, list(range(0, dbms.shape[1], 3)), axis=1)
    #print "  dbms.shape: " + str(dbms.shape)
    overalldbs = np.append( overalldbs,dbms,1 )
    #print "  overalldbs.shape: " + str(overalldbs.shape)
    print ("file " + str(cntfil) + " of " + str(howmany) )

print ("\noveralldbs.shape: " + str(overalldbs.shape))
metaRows, metaCols = overalldbs.shape
while metaCols > maxcols:
    print ("...reducing...")
    overalldbs = np.delete(overalldbs, list(range(0, overalldbs.shape[1], 6)), axis=1)
    metaRows, metaCols = overalldbs.shape

print ("overalldbs.shape: " + str(overalldbs.shape))
print("...plotting...")

overalldbs = np.flipud(overalldbs)

startFreq = startFreq - radioConfig.upconvFreqHz
endFreq = endFreq - radioConfig.upconvFreqHz

cropRelatedReduction = ( int(cropExcludedBins) / 2 ) * stepFreq

startFreq = startFreq + cropRelatedReduction
endFreq = endFreq - cropRelatedReduction

outname = sessionfolder + os.sep + "wholesession-" + sessionfolder

iniTime = to_datetime_from_utc(time.strptime(absfirstAcqTimestamp, "%Y-%m-%d %H:%M:%S"))
endTime = to_datetime_from_utc(time.strptime(lastAcqTimestamp, "%Y-%m-%d %H:%M:%S"))
x_lims = (iniTime, endTime)
tRange = mdates.date2num(x_lims)
inix, endx = tRange
fRange = (startFreq, endFreq)

theExtent = [ inix, endx, startFreq, endFreq ]

fig,ax = plt.subplots(figsize=(11.69,8.27), dpi=100)
imgax = specview.RFshow(overalldbs, ax, cmap=cmapname, cmap_norm='equalize', hs=False, colorbar=True, cb_ticks='stats', nSigma=2, extent=theExtent, origin='lower', aspect='auto', fRange=fRange, FFTbins=metaRows )

plt.title("Overall session", fontsize = 10)

plt.tight_layout()

#plt.show()
fig.savefig(outname, dpi=300)
print("Whole session plot completed.")

del fig
del overalldbs
del dbms

# load image and get size info
old_im = Image.open(outname + '.png')
old_size = old_im.size
ow, oh = old_im.size

print("...performing palette conversion...")
# this is necessary to keep image file size at a minimum
# ( it's also the file mode used by gnuplot )
new_im = old_im.convert('P', palette=Image.ADAPTIVE, colors=256)

print("...adding metadata to image...")
# create and attach info dictionary with metadata
meta = PngImagePlugin.PngInfo()
meta.add_text("ra-stationID", radioConfig.stationID)
meta.add_text("ra-scanTarget", radioConfig.scanTarget)
meta.add_text("ra-FFTbins", str(metaCols))
meta.add_text("ra-FreqStart", str(startFreq))
meta.add_text("ra-FreqEnd", str(endFreq))
meta.add_text("ra-FreqStep", str(stepFreq))
meta.add_text("ra-avgScanDur", str(avgScanDur))
meta.add_text("ra-scanTimestampFirst", absfirstAcqTimestamp)
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
print("...annotated plot saved.")
