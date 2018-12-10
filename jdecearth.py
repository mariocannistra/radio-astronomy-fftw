#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# this program will output the Jupiter-IO radio storm predictions in text format. 
# It's a port to python of an older QBasic program whose original source can be found 
# at http://www.spaceacademy.net.au/spacelab/projects/jovrad/jovrad.htm together with 
# good explanations about the theory and instructions to build a folded dipole antenna.

import raforpi
from skyfield.api import load
import sys
from datetime import datetime, timedelta
from pytz import timezone
import radioConfig
from dateutil.relativedelta import relativedelta

# the section below needs deeper check on the involved formulas:
print('\nJovicentric Declination of Earth: (to be checked)')
eph = load('jup310.bsp')
jupiter = eph['jupiter']
earth = eph['earth']

deyear = 2000
while deyear < 2020:
	initDateUTC = load.timescale().utc(deyear, 1, 1, 0.0, 0.0, 0.0 )
	geometry = jupiter.at( initDateUTC ).observe(earth)
	jcera, jcedec, jcedist = geometry.radec()
	jcinfo = 'year {}\tjcedec {}'.format( initDateUTC.utc_datetime().strftime('%Y%m%d'), jcedec )
	print(jcinfo)
	deyear = deyear + 1
