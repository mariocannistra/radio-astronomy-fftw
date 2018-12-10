#!/bin/sh
# this is the main script to run a radio scan session
# it will temporarily pause the NTPd daemon to force a time sync with
# your preferred "geographically local" server using the ntpdate command
# why ? because if you just switched on the R-PI the NTPd daemon has not
# done th sync with servers YET, it would do that soon (couple of mins ?)
# but should you want to run the scan automatically at boot up... you need this
#
# it will then spawn the execution of a python script in a detached session
# so that you can then logout from the R-PI console and leave it running
#
# once you see the nohup message you just have to hit enter to be able to
# enter commands or to logout
#
# when you will log in after few hours you will be able to check the folder
# content and session status
echo 'stopping ntpd'
sudo service ntp stop
echo 'forcing time sync'
sudo ntpdate -vd ntp1.inrim.it
echo 'starting ntpd'
sudo service ntp start
ntpq -p
cd /home/pi/radio-astronomy-fftw
# rm nohup.out
echo 'starting radio scan session'
nohup python doscanw.py &
