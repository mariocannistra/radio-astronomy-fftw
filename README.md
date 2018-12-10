# radio-astronomy-fftw

**This is version 9 (May 7, 2018) of my radio-astronomy data collection and dissemination project.**  

Please note that starting from version 9 this sw makes usage of latest Skyfield version (1.3). 
You can install using **pip install skyfield**
It is no longer necessary to install using **pip install skyfield==0.6.1**

**The programs use [a modified version of rtl_power_fftw](https://github.com/mariocannistra/rtl-power-fftw) originally written by Klemen Blokar and Andrej Lajovic.**  

There is a [Windows binary release of rtl_power_fftw available for download](https://github.com/mariocannistra/rtl-power-fftw/releases)  

The following diagram and document are still aligned with version 3. Will soon update them for version 4 and 5 changes.

A diagram showing the interactions between the various programs is available [here](https://raw.githubusercontent.com/mariocannistra/radio-astronomy-fftw/master/doc/observ-sw-diagram.png)  

Full documentation of the software setup and config for the various programs and tools is [here](doc/sw-setup.pdf)  

**All this sw has been changed/written, built and tested on a Raspberry PI 2 and then installed and re-tested on a Raspberry PI 3.**  

See project website at https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617  

This system has been designed for amateur radio-astronomers to receive radio signals and perform related data collection and dissemination.  
Radio emissions from sky sources like Sun and Jupiter can be received and converted to digital domain for processing.  
Data and/or processing results are pushed to AWS for storage and dissemination.  
Multiple low-cost receiver-processors are envisioned around the globe connecting centrally to distribute to any interested subscriber with an IoT like approach.  
An open science initiative with a strong collaborative approach to large scale measurement of natural events.  

Hardware used:  
Raspberry PI 3 (2 works fine obviously), RTL SDR radio receiver, dipole antenna and other radio accessories  

Also used by this project: AWS authentication, messaging gateway plus other processing and storage services (IoT, S3, ..)  
