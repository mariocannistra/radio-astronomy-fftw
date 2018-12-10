# -*- coding: utf-8 -*-
"""
code protions from hillshading routines by Joseph Barraud, Geophysics Labs.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from skimage import exposure

import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

def fmtMHz(x, pos):
	'The two args are the value and tick position'
	return '%1.2f' % (x*1e-6)

def cmap_to_array(cmap,N=256):
	"""
	Return a Nx3 array of RGB values generated from a colormap.
	"""
	return cmap(np.linspace(0, 1, N))[:,:3] # remove alpha column

def equalizeColormap(cmap,bins,cdf,name='EqualizedMap'):
	'''
	Re-map a colormap according to a cumulative distribution. This is used to 
	perform histogram equalization of an image by changing the colormap 
	instead of the image. *This is not strickly speaking the equalization of the 
	colormap itself*.
	The cdf and bins should be calculated from an input image, as if carrying out
	the histogram equalization of that image. In effect, the cdf becomes integrated  
	to the colormap as a mapping function by redistributing the indices of the
	input colormap.

	Parameters
	----------
	cmap : string or colormap object
		Input colormap to remap.
	bins : array
		Centers of bins.
	cdf : array
		Values of cumulative distribution function.
	'''

	# first retrieve the color table (lists of RGB values) behind the input colormap
	if cmap in cm.cmap_d: # matplotlib colormaps + plus the new ones (viridis, inferno, etc.)
		cmList = cmap_to_array(cm.cmap_d[cmap])
	else:
		try:
			# in case cmap is a colormap object
			cmList = cmap_to_array(cmap) 
		except:
			raise ValueError('Colormap {} has not been recognised'.format(cmap))

	# normalize the input bins to interval (0,1)
	bins_norm = (bins - bins.min())/np.float(bins.max() - bins.min())

	# calculate new indices by applying the cdf as a function on the old indices
	# which are initially regularly spaced. 
	old_indices = np.linspace(0,1,len(cmList))
	new_indices = np.interp(old_indices,cdf,bins_norm)

	# make sure indices start with 0 and end with 1
	new_indices[0] = 0.0
	new_indices[-1] = 1.0

	# remap the color table
	cdict = {'red': [], 'green': [], 'blue': []}
	for i,n in enumerate(new_indices):
		r1, g1, b1 = cmList[i]
		cdict['red'].append([n, r1, r1])
		cdict['green'].append([n, g1, g1])
		cdict['blue'].append([n, b1, b1])

	return mcolors.LinearSegmentedColormap(name, cdict)

def stats_boundaries(data,nSigma=1,sigmaStep=1):
	'''
	Return a list of statistical values ordered in increasing order that can
	be used for ticks or boundaries.
	'''
	mu = np.nanmean(data)
	sigma = np.nanstd(data)
	newTicks = mu + sigma*np.arange(-nSigma,nSigma+sigmaStep,sigmaStep)

	return [np.nanmin(data)] + newTicks.tolist() + [np.nanmax(data)]

def RFshow(data,ax=None,cmap='RdYlBu',cmap_norm='equalize',hs=True,
              zf=10,azdeg=45,altdeg=45,dx=1,dy=1,fraction=1.5,blend_mode='alpha',
              alpha=0.7,contours=False,levels=32,colorbar=True,cb_contours=False,
              cb_ticks='linear',nSigma=1,fRange=None,FFTbins=512,**kwargs):

    # equalize the colormap:
    cdf, bins = exposure.cumulative_distribution(data[~np.isnan(data)].flatten(),nbins=256)
    my_cmap = equalizeColormap(cmap,bins,cdf)

    # convert input data to masked array
    data = np.ma.masked_array(data, np.isnan(data))

    fig = ax.get_figure()

    im = ax.imshow(data,cmap=my_cmap,**kwargs)

    # time axis:
    ax.xaxis_date()
    xxstart, xxend = ax.get_xlim()
    # we want 11 ticks:
    ax.xaxis.set_ticks(np.linspace(xxstart, xxend, 11, endpoint=True))
    #ax.set_xticklabels(np.linspace(xxstart, xxend, 11, endpoint=True))
    date_format = mdates.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(date_format)
    # fig.autofmt_xdate()
    for tick in ax.get_xticklabels():
    	tick.set_rotation(90)

    # frequencies axis:
    # we want 11 ticks:
    plt.yticks(np.linspace(fRange[0], fRange[1], 11, endpoint=True))
    yformatter = FuncFormatter(fmtMHz)
    ax.yaxis.set_major_formatter(yformatter)

    plt.xlabel('UTC time', labelpad=10)
    plt.ylabel('FFT frequencies in MHz (over %d bins)' % (FFTbins) )

    # colorbar:
    newTicks = stats_boundaries(data,nSigma,nSigma)
    cb1 = fig.colorbar(im,ticks=newTicks)

    cb1.ax.set_xlabel('relative\npower', labelpad=10)

    cb1.update_normal(im)
