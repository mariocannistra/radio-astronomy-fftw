#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# this program will output the Jupiter-IO radio storm predictions in text format. 
# It's a port to python of an older QBasic program whose original source can be found 
# at http://www.spaceacademy.net.au/spacelab/projects/jovrad/jovrad.htm together with 
# good explanations about the theory and instructions to build a folded dipole antenna.

#  usage: jpredict.py [-h] [-s [INITIALDATE]] [-d [PREDICTDAYS]]
#                     [-i [INCLUDEONLYIORELATED]]
#  
#  optional arguments:
#    -h, --help            show this help message and exit
#    -s [INITIALDATE], --initialDate [INITIALDATE]
#                          YYYYMMDD - start date of prediction days - default
#                          current date
#    -d [PREDICTDAYS], --predictDays [PREDICTDAYS]
#                          number - search predictions for specified days from
#                          start date - default defined in radioConfig.py
#    -i [INCLUDEONLYIORELATED], --includeOnlyIOrelated [INCLUDEONLYIORELATED]
#                          Y/N - return predictions only for Io related events -
#                          default defined in radioConfig.py
#
#  example:  python jpredict.py -s 20180512 -d 3 -i Y
#

import raforpi
from skyfield.api import load
import sys
from datetime import datetime, timedelta
from pytz import timezone
import radioConfig
import argparse

#modeset = 1
modeset = 2     # I've found this set to be close to Radio Jupiter Pro results, will check again in the future
#modeset = 3

calcinterval = radioConfig.calcinterval
prefLocal = radioConfig.prefLocal	# False = output in UTC  -  True = output in local observatory time zone

def valid_date(s):
	try:
		chkdate = datetime.strptime(s, "%Y%m%d")
		return s
	except ValueError:
		msg = "Not a valid date: '{0}'.".format(s)
		raise argparse.ArgumentTypeError(msg)

def validyesno(s):
	s = s.upper()
	if s == 'Y':
		return True
	if s == 'N':
		return False
	msg = "Not a valid Y/N argument"
	raise argparse.ArgumentTypeError(msg)

parser = argparse.ArgumentParser()

parser.add_argument('-s', "--initialDate", nargs='?', const=1, default=datetime.now().strftime('%Y%m%d'), type=valid_date, required=False, help="YYYYMMDD  - start date of prediction days - default current date")

parser.add_argument('-d', "--predictDays", nargs='?', const=1, default=radioConfig.predictdays, type=int, required=False, help="number  - search predictions for specified days from start date - default defined in radioConfig.py")

parser.add_argument('-i', "--includeOnlyIOrelated", nargs='?', const=1, default=radioConfig.includeonlyiorelated, type=validyesno, required=False, help="Y/N  - return predictions only for Io related events - default defined in radioConfig.py")

args = parser.parse_args()

initialDate = args.initialDate
predictDays = args.predictDays
includeOnlyIOrelated = args.includeOnlyIOrelated

predictions = raforpi.predictStorms(initialDate, predictDays, includeOnlyIOrelated, calcinterval, modeset)

obsTime = timezone( radioConfig.stationTimezone )

def utc2tz(thetime):
	global obsTime
	return thetime.astimezone(obsTime)

if prefLocal == True:
	print('local time\t\tCML III\t\tIO phase\tSource\tJupiter Rise-Set (local)\t\t\tSun Rise-Set (local)')
else:
	print('UTC time\t\tCML III\t\tIO phase\tSource\tJupiter Rise-Set (UTC)\t\t\t\tSun Rise-Set (UTC)')

for pred in predictions:
	if prefLocal == True:
		evtDetail = '{}\t\t{:06.2f}\t\t{:06.2f}\t\t{}\t{} {}\t\t\t{} {}'.format( utc2tz(pred.predts).strftime('%b %d %H:%M:%S'), pred.CML3, pred.ioPhase, pred.source, utc2tz(pred.jupRise).strftime('%b %d %H:%M:%S'), utc2tz(pred.jupSet).strftime('%b %d %H:%M:%S'), utc2tz(pred.sunRise).strftime('%b %d %H:%M:%S'), utc2tz(pred.sunSet).strftime('%b %d %H:%M:%S') )
	else:
		evtDetail = '{}\t\t{:06.2f}\t\t{:06.2f}\t\t{}\t{} {}\t\t\t{} {}'.format( pred.predts.strftime('%b %d %H:%M:%S'), pred.CML3, pred.ioPhase, pred.source, pred.jupRise.strftime('%b %d %H:%M:%S'), pred.jupSet.strftime('%b %d %H:%M:%S'), pred.sunRise.strftime('%b %d %H:%M:%S'), pred.sunSet.strftime('%b %d %H:%M:%S') )
	print( evtDetail )
