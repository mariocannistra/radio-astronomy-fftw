#! /usr/bin/env python

from skyfield.api import load, JulianDate, utc, now
from pytz import timezone
import radioConfig

print
print "Configured time zone: %s" % (radioConfig.stationTimezone)

mytz = timezone(radioConfig.stationTimezone)
jd = now()
jdutc = jd.utc_datetime()
print "UTC         : %s" % (jdutc)

jd = JulianDate(utc=jdutc)
dt = jd.astimezone(mytz)
print "My timezone : %s" % (dt)
print

