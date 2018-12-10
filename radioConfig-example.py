# scan parameters configured here
# are used by all the scripts

freqCenter = 21000000   # example: if you want to scan from 17 to 25 MHz you enter here 21000000 as center frequency and 8000000 below as bandwidth
freqBandwidth = 8000000
upconvFreqHz = 125000000    # this is your upconverter offset frequency in Hz, set to 0 if you're not using an upconverter

# maximum value successfully tested on the R-PI-3 : 2800000
rtlSampleRateHz = 2000000

# specify one of the two values and set the other to 0
totalFFTbins = 4000	# this is the total number of bins available on a scan. will be divided by number of necessary hops and is affected by crop percenteage

binSizeHz = 0 # this is the FFT bin size in Hz, lower values will give you more detail in spectrograms, but larger files to process on the R-PI

# Specify the percentage of bins to be discarded on each scan.
# It will actually be half on each side of a single scan.
cropPercentage = 30

# specify one of the two values and set the other to 0
integrationIntervalSec = 0.5	# see rtl_power_fftw documentation, this is the integration time in seconds. can be < 1 sec 
integrationScans = 0	# see rtl_power_fftw documentation, this is the number of scans that will be averaged for integration purposes. Allows to integrate for less than 1 second.

subtractBaseline = False   # when true a previously recorded baseline scan will be subtracted from every scan before saving to disk

gain = 30   # maximum gain is about 49, can be too much in certain positions with strong interfering sources
linearPower = False	# flag to calculate linear power values instead of logarithmic
tunerOffsetPPM = 0 # see rtl_power documentation, i can use 0 on my TCXO based dongle, cab be anything from 0 to 60 or more depending on the dongle (use kalibrate to find it out)
dataGatheringDurationMin = 30   # duration of single scan in minutes. 30 minutes is the suggested duration for better chart and limit on memory available on R-PI
sessionDurationMin = 600    # overall session duration in minutes 10 hours = 10 * 60 = 600
scanTarget = "Jupiter"  # this string will be used to create a subfolder under which all sessions spectrograms will be stored (one subfolder per each date)
# the following observer position is used by Jupiter-Io radio emission
# prediction utility  jpredict.py  to calculate Jupiter apparent position / visibility
# for your site:
stationID = "myObservatoryNameOrAcronym"
stationTimezone = "Europe/Rome"
stationLat = "00.00000 X"  # enter your station latitude here with this string format "00.00000 X"  where X is either N or S (North or Sud)
stationLon = "00.00000 X"  # enter your station longitude here with this string format "00.00000 X"  where X is either E or W (East or West)
stationElev = 0   # enter your station elevation in meters (above sea level)
#
predictdays = 5
includeonlyiorelated = False
calcinterval = 15
prefLocal = True	# False = output in UTC  -  True = output in local observatory time zone
#
plotWaterfall = True
generateThumbs = False
uploadToS3 = False	# if you want to upload your scans
sendIoTmsg = False  # if you want to send notifications. Please, get in touch with me to get the certificates in order to send mqtt notifications
# do not change the following lines:
awshost = "data.iot.eu-west-1.amazonaws.com"
awsport = 8883
clientId = "mcawsthings-test2"
thingName = "mcawsthings-test2"
caPath = "./aws-iot-rootCA.crt"
certPath = "./cert.pem"
keyPath = "./privkey.pem"
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
