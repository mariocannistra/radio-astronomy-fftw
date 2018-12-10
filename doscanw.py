#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# to start a scan session you MUST enter:    bash runw.sh
# runw.sh is the shell script that will start this python program in the proper way

# BEFORE RUNNING THIS PROGRAM please set your configuration values in file  radioConfig.py

# this program executes the radio scans using rtl_power_fftw by Klemen Blokar and Andrej Lajovic
# in parallel with rtl_power_fftw, it will run  postprocw.py  that will produce the spectrograms,
# upload to AWS S3 if enabled, send mqtt notifications if enabled

# at the end of session it will run also  findsessionrangew.py  that will determine the overall
# range of signal strengths received during the whole session. Its output will be stored in 2 files:
# dbminmax.txt and session-overview.png . The first contains two rows of text with just the maximum
# and minimum of the whole session. The second contains a chart of all the min and max values for each of
# the scan files

from datetime import datetime
import subprocess
import os
import sys
import radioConfig
from math import ceil
import shutil
from scipy import signal

def make_sure_path_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        shutil.copyfile("./radioConfig.py", "./" + directory + "/radioConfig.py")

cmdstring = "rtl_power_fftw"

sessiondate = datetime.utcnow().strftime('%Y%m%d')
#create folder if does not exist yet:
make_sure_path_exists(sessiondate)


freqstart = radioConfig.freqCenter - (radioConfig.freqBandwidth/2) + radioConfig.upconvFreqHz
freqstop  = radioConfig.freqCenter + (radioConfig.freqBandwidth/2) + radioConfig.upconvFreqHz
sfreqstart = '%0.3fM' % (freqstart/1000000.0)
sfreqstop = '%0.3fM' % (freqstop/1000000.0)

if radioConfig.totalFFTbins > 0:
    freqbins = radioConfig.totalFFTbins
else:
    freqbins = int((freqstop - freqstart) / radioConfig.binSizeHz)

min_overhang = float(radioConfig.rtlSampleRateHz) * radioConfig.cropPercentage / 100;
hops = ceil((float(freqstop - freqstart) - min_overhang) / (float(radioConfig.rtlSampleRateHz) - min_overhang));

binReduxPerc = (100 - radioConfig.cropPercentage) / 100.0

if hops > 1:
    freqbins = int( freqbins / hops )

if (freqbins & 1) == 1:	# check if odd
    freqbins = freqbins + 1
totalFFTbins = int(freqbins*binReduxPerc) * hops
print("\n[INFO] freqbins,hops,binReduxPerc,totalFFTbins: ",freqbins,hops,binReduxPerc,totalFFTbins)
print("\n")

datagathduration = str(radioConfig.dataGatheringDurationMin) + "m"
truefreqstart = '%0.3fM' % ((radioConfig.freqCenter - (radioConfig.freqBandwidth/2))/1000000.0)
truefreqstop  = '%0.3fM' % ((radioConfig.freqCenter + (radioConfig.freqBandwidth/2))/1000000.0)

cmdstring = cmdstring + " -f " + str(freqstart)
cmdstring = cmdstring + ":" + str(freqstop)

cmdstring = cmdstring + " -r " + str(radioConfig.rtlSampleRateHz)

cmdstring = cmdstring + " -b " + str(freqbins)

if radioConfig.integrationIntervalSec > 0:
    cmdstring = cmdstring + " -t " + str(radioConfig.integrationIntervalSec)
    #cmdstring = cmdstring + " -T"
else:
    cmdstring = cmdstring + " -n " + str(radioConfig.integrationScans)

cmdstring = cmdstring + " -g " + str(radioConfig.gain * 10)

cmdstring = cmdstring + " -p " + str(radioConfig.tunerOffsetPPM)

if radioConfig.cropPercentage > 0:
    cmdstring = cmdstring + " -x " + str(radioConfig.cropPercentage)

cmdstring = cmdstring + " -e " + datagathduration
cmdstring = cmdstring + " -q"

if radioConfig.linearPower:
    cmdstring = cmdstring + " -l"

if radioConfig.fftWindow != "":
    if radioConfig.fftWindow == "BlacHarr":
        window = signal.blackmanharris(freqbins)
    elif radioConfig.fftWindow == "DolpCheb":
        window = signal.chebwin(freqbins, at=80)
    elif radioConfig.fftWindow == "FlatTop":
        window = signal.flattop(freqbins)

    file = open("window.txt","w")
    for wparm in window:
        file.write('{0:.12f}\n'.format(wparm))
    file.close() 
    cmdstring = cmdstring + " -w window.txt"

if radioConfig.sessionDurationMin == 0:
    loopForever = True
else:
    loopForever = False

numscans = radioConfig.sessionDurationMin / radioConfig.dataGatheringDurationMin

scancnt = 1
continueLoop = True
postprocrunning = False
while continueLoop:
    scantimestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')

    #build scan filename
    scanname = "UTC" + scantimestamp + "-" + radioConfig.stationID + "-" + radioConfig.scanTarget + "-" + truefreqstart + "-" + truefreqstop + "-b" + str(totalFFTbins)

    if radioConfig.integrationIntervalSec > 0:
        scanname = scanname + "-t" + str(radioConfig.integrationIntervalSec)
    else:
        scanname = scanname + "-n" + str(radioConfig.integrationScans)

    scanname = scanname + "-g" + str(radioConfig.gain) + "-e" + datagathduration
    if radioConfig.notes:
        scanname = scanname + "-" + radioConfig.notes

    if radioConfig.fftWindow != "":
        scanname = scanname + "-" + radioConfig.fftWindow

    completecmdstring = cmdstring + " -m " + sessiondate + os.sep + scanname

    print(completecmdstring)

    print('\nrunning scan n. %d  (%d hops per scan)\n' % (scancnt, hops))
    #print(completecmdstring)
    #run the scan and wait for completion
    scanp = subprocess.Popen(completecmdstring, shell = True)
    #os.waitpid(scanp.pid, 0)
    scanp.wait()
    if scanp.returncode != 0:
        print('Error running the radio scan sw.\n')
        print('Session interrupted.')
        sys.exit(0)

    if loopForever == False:
        print('Completed scan %d of %d\n' % (scancnt,numscans))
    else:
        print('Completed scan %d\n' % (scancnt))

    #get event probability info
    #process the scan adding probability info

    if radioConfig.plotWaterfall:
        chartcmdstring = "python postprocw.py " + scanname + " 0.0 0.0 " + sessiondate
        #run rendering WITHOUT waiting for completion
        genchrtp = subprocess.Popen(chartcmdstring, shell = True)
        postprocrunning = True

    # go on with next scan:
    if loopForever == False:
        scancnt = scancnt + 1
        if scancnt > numscans:
            continueLoop = False
    else:
        scancnt = scancnt + 1

#if postprocrunning == True:
#    genchrtp.wait()	# wait for last plot to complete, just in case

sessrngcmdstring = "python findsessionrangew.py " + sessiondate
sessrng = subprocess.Popen(sessrngcmdstring, shell = True)
sessrng.wait()
