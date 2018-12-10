#!/usr/bin/python

# BSL = Bright surge on the limb
# DSF = Filament disappearance
# EPL = Eruptive prominence on the limb
# FIL = Filament
# FLA = Optical flare observed in H-alpha 
# FOR = Forbush decrease (cosmic ray decrease))
# GLE = Ground-level event (cosmic ray increase)
# LPS = Loop prominence system
# PCA = Polar cap absorption
# RBR = Fixed-frequency radio burst
# RNS = Radio Noise Storm
# RSP = Sweep-frequency radio burst
# SPY = Spray
# XFL = SXI X-ray flare from GOES Solar X-ray Imager (SXI)
# XRA = X-ray event from SWPC's Primary or Secondary GOES spacecraft

import urllib.request
from datetime import datetime
import sys

if len(sys.argv) == 2:
	todaydate = sys.argv[1]
else:
	todaydate = datetime.utcnow().strftime('%Y%m%d')

url = 'ftp://ftp.swpc.noaa.gov/pub/indices/events/' + todaydate + 'events.txt'
print('Retrieving: ' + url)

response = urllib.request.urlopen(url)
data = response.read()
events = data.decode('utf-8')

eventlines = events.splitlines()

chars = set(':#N')	# not interested in comments and "NO EVENT REPORTS."
evtfilter = ['RBR', 'RNS', 'RSP', 'XFL', 'XRA', 'FLA']	# interested in these event types only
longevt = ['XRA', 'FLA']

print( 'Filtering on: ' + ",".join(evtfilter) )

def prsutctime(rawtime):
	if rawtime == '////':
		utctim = '////////'
	else:
		utctim = rawtime[0:2] + ':' + rawtime[2:] + ':00'
	return utctim

with open( 'evts' + todaydate + '.txt', "w") as text_file:
	for line in eventlines:
		if line != '':	# skip empty lines
			line = line.replace('+',' ')	# strip away the plus to avoid item n. issues in following lines
			linefields = line.split()
			if (linefields[0][0] in chars) == False:	# this will skip comments and "NO EVENT REPORTS."
				if linefields[6] in evtfilter:	# this will catch our events
					initime = prsutctime( linefields[1] )
					maxtime = prsutctime( linefields[2] )
					endtime = prsutctime( linefields[3] )
					sevt = "%s %s %s %s %s %s %s %s" % ( initime, maxtime, endtime, linefields[0], linefields[4], linefields[6], linefields[7], linefields[8] )
					if linefields[6] in longevt:
						sevt = sevt + ' ' + linefields[9]
					print( sevt )
					text_file.write( sevt + '\n' )
