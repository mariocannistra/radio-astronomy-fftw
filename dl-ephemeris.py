#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# this program will download and/or test the JPL ephemerides using
# the python package SkyField by Brandon Rhodes
# the 2 files are about 1 GB in size, please refer to the project
# description at the following url for more information on how to 
# download them directly

# your geographical position and timezone should be previously set in file:  radioConfig.py

from skyfield.api import load
from datetime import datetime
from pytz import timezone
from skyfield.api import now
import radioConfig

planets = load('de421.bsp')
earth, jupiter = planets['earth'], planets['jupiter barycenter']

jd = now()
rome = timezone(radioConfig.stationTimezone)
dt = jd.astimezone(rome)

print('\nUTC:  ' + str(jd.utc_datetime()))
print('Local: ' + str(dt))

print('\nJupiter position from my lat-long:')
myposition = earth.topos(radioConfig.stationLat, radioConfig.stationLon)
position = myposition.at(utc=(2015, 12, 14, 21,0,0 )).observe(jupiter)
print(position.apparent().radec())

# 1) the central meridian longitude of Jupiter that faces us
# 2) the position of the inner-most moon Io in its orbit around Jupiter
# 3) the Jovicentric declination of the Earth

eph = load('jup310.bsp')

print('\nIo position around Jupiter:')
# 2):
jupiter = eph['jupiter']
io = eph['io']
geometry = jupiter.at(utc=(2015, 12, 14, 21,0,0 )).observe(io)
#print(geometry.position.au)
print(geometry.radec())

print(jupiter)

print('\nJovicentric Declination of Earth:')
# 3):
jupiter = eph['jupiter']
earth = eph['earth']
geometry = jupiter.at(utc=(2015, 12, 14, 21,0,0 )).observe(earth)
#print(geometry.position.au)
print(geometry.radec())
