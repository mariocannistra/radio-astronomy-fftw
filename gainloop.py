#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# BEFORE RUNNING THIS PROGRAM please set your configuration values in file  radioConfig.py

# this program executes the radio scans just like doscanw.py but will iterate through all the possible gain values and reuse each time all the other parameters
# in this way it will be possible to visualize the different power ranges that can be measured in the same receiver/antenna conditions/configuration varying the receiver gain.   It could be a useful tool in selecting a gain that is not too high or low and possibly avoid the cross modulation effects

# At the end of session it will run  findsessionrangew.py  that will determine the overall
# range of signal strengths received during the whole session. Its output will be stored in 2 files:
# dbminmax.txt and session-overview.png . The first contains two rows of text with just the maximum
# and minimum of the whole session. The second contains a chart of all the min and max values for each of
# the scan files

from datetime import datetime
import subprocess
import os
import radioConfig
import numpy as np
import math

availgains = np.array( [ 9, 14, 27, 37, 77, 87, 125, 144, 157, 166, 197, 207, 229, 254, 280, 297, 328, 338, 364, 372, 386, 402, 421, 434, 439, 445, 480, 496 ] )

# 328-338-364
# these are the 3 best gain values found on first run, 20.1 MHz and stylus antenna, without LNA

for ggg in availgains:

	cmdstring = "rtl_power_fftw"

	freqstart = radioConfig.freqCenter - (radioConfig.freqBandwidth/2) + radioConfig.upconvFreqHz
	freqstop  = radioConfig.freqCenter + (radioConfig.freqBandwidth/2) + radioConfig.upconvFreqHz
	sfreqstart = '%0.3fM' % (freqstart/1000000.0)
	sfreqstop = '%0.3fM' % (freqstop/1000000.0)

	if radioConfig.totalFFTbins > 0:
		freqbins = radioConfig.totalFFTbins
	else:
		freqbins = (freqstop - freqstart) / radioConfig.binSizeHz

	hops = math.ceil( float(freqstop - freqstart) / float(radioConfig.rtlSampleRateHz) )
	if hops > 1:
		freqbins = int( freqbins / hops )
		totalFFTbins = int(freqbins * hops)
	else:
		totalFFTbins = int(freqbins)

	datagathduration = str(radioConfig.dataGatheringDurationMin) + "m"
	truefreqstart = '%0.3fM' % ((radioConfig.freqCenter - (radioConfig.freqBandwidth/2))/1000000.0)
	truefreqstop  = '%0.3fM' % ((radioConfig.freqCenter + (radioConfig.freqBandwidth/2))/1000000.0)

	cmdstring = cmdstring + " -f " + str(freqstart)
	cmdstring = cmdstring + ":" + str(freqstop)

	cmdstring = cmdstring + " -r " + str(radioConfig.rtlSampleRateHz)

	cmdstring = cmdstring + " -b " + str(freqbins)

	if radioConfig.integrationIntervalSec > 0:
		cmdstring = cmdstring + " -t " + str(radioConfig.integrationIntervalSec)
		cmdstring = cmdstring + " -T"
	else:
		cmdstring = cmdstring + " -n " + str(radioConfig.integrationScans)

	cmdstring = cmdstring + " -g " + str( ggg )

	cmdstring = cmdstring + " -p " + str(radioConfig.tunerOffsetPPM)

	if radioConfig.cropPercentage > 0:
		cmdstring = cmdstring + " -x " + str(radioConfig.cropPercentage)

	cmdstring = cmdstring + " -e " + datagathduration
	cmdstring = cmdstring + " -q"

	if radioConfig.linearPower:
		cmdstring = cmdstring + " -l"

	scantimestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')

    #build scan filename
	scanname = "UTC" + scantimestamp + "-" + radioConfig.stationID + "-" + radioConfig.scanTarget + "-" + truefreqstart + "-" + truefreqstop + "-b" + str(totalFFTbins)

	if radioConfig.integrationIntervalSec > 0:
		scanname = scanname + "-t" + str(radioConfig.integrationIntervalSec)
	else:
		scanname = scanname + "-n" + str(radioConfig.integrationScans)

	scanname = scanname + "-g" + str( ggg ) + "-e" + datagathduration

	completecmdstring = cmdstring + " -m " + sessiondate + os.sep + scanname

	print('running scan with gain %s' % (ggg))
	print(completecmdstring)

	#run the scan and wait for completion
	scanp = subprocess.Popen(completecmdstring, shell = True)
	#os.waitpid(scanp.pid, 0)
	scanp.wait()

	#get event probability info
	#process the scan adding probability info

	chartcmdstring = "python postprocw.py " + scanname + " 0.0 0.0 " + sessiondate
	#run gnuplot WITHOUT waiting for completion
	genchrtp = subprocess.Popen(chartcmdstring, shell = True)

	print('processing complete for scan with gain %s' % (ggg))

chartcmdstring = "python findsessionrangew.py " + sessiondate
genchrtp = subprocess.Popen(chartcmdstring, shell = True)
