#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Time-stamp: <2021/07/03 15:50:42 (JST) maeda>

import os
import numpy as np
import re
from astropy.io import fits
from astropy.time import Time
import subprocess
import glob
import sys
import lsst.afw.image as afwImage

## mode selection ####
mode = input("Please choose binning mode.\n (2: 2x2 binning, 4: 4x4 binning):")
if   mode=="2":
    print ("2x2 binning mode.")
    nbin = 2
elif mode=="4":
    print ("4x4 binning mode.")
    nbin = 4
else:
    print ("ERROR: invarid binning mode. Please input 2 or 4.")
    sys.exit()
########################

# search fits files
img_list = sorted(glob.glob('warp-*.fits'))

for i in img_list[0:5]:
    hdu1 = fits.open(i)
    xpix = hdu1[1].header['NAXIS1']
    ypix = hdu1[1].header['NAXIS2']
    scidata  = hdu1[1].data  # science-image
    maskdata = hdu1[2].data  # mask-image

#bining
#mean(?) ? is axis number.-1 means horizontal. 1 means vertical.
    scidata_bin  = scidata.reshape(int(ypix/nbin), nbin, int(xpix/nbin), nbin).mean(-1).mean(1)
    maskdata_bin = maskdata.reshape(int(ypix/nbin), nbin, int(xpix/nbin), nbin).mean(-1).mean(1)
    
#make header
#obs time
#S.U edit
#    t1 = Time(hdu1[0].header['TIME-MID'],format='isot',scale='utc')  
    t1 = Time(hdu1[0].header['DATE-AVG'],format='isot',scale='utc')  
    hdu1[0].header['JD'] = t1.jd
#zero_point = 2.5 *np.log10(Fluxmag0), mag = zero_point - 2.5 * np.log10(flux)
#FLUXMAG0ERR is 10^{-4} mag. Negligible"
    exp = afwImage.ExposureF(i)
    pc = exp.getPhotoCalib()
    FLUXMAG0 = pc.getInstFluxAtZeroMagnitude()
    zerop1 = 2.5 * np.log10(FLUXMAG0)
#    ref_flux = 1.0e23*1.0e9*10**(-0.4*48.6)
#    FLUXMAG0ERR = FLUXMAG0 * pc.getCalibrationErr()/pc.getCalibrationMean()
#    print(FLUXMAG0,zerop1,FLUXMAG0ERR,zero)
    hdu1[0].header['Z_P'] = zerop1
#    hdu1[0].header['EQUINOX'] = hdu1[1].header['EQUINOX']
    hdu1[0].header['RADESYS'] = hdu1[1].header['RADESYS']
    hdu1[0].header['CRPIX1'] =  hdu1[1].header['CRPIX1']/nbin
    hdu1[0].header['CRPIX2'] =  hdu1[1].header['CRPIX2']/nbin
    hdu1[0].header['CD1_1'] =  hdu1[1].header['CD1_1']*nbin
    hdu1[0].header['CD1_2'] =  hdu1[1].header['CD1_2']
    hdu1[0].header['CD2_1'] =  hdu1[1].header['CD2_1']
    hdu1[0].header['CD2_2'] =  hdu1[1].header['CD2_2']*nbin
    hdu1[0].header['CRVAL1'] = hdu1[1].header['CRVAL1']
    hdu1[0].header['CRVAL2'] = hdu1[1].header['CRVAL2']
#    hdu1[0].header['CUNIT1'] = hdu1[1].header['CUNIT1']
#    hdu1[0].header['CUNIT2'] = hdu1[1].header['CUNIT2']
    hdu1[0].header['CTYPE1'] = hdu1[1].header['CTYPE1']
    hdu1[0].header['CTYPE2'] = hdu1[1].header['CTYPE2']
    hdu1[0].header['LTV1'] = hdu1[1].header['LTV1']
    hdu1[0].header['LTV2'] = hdu1[1].header['LTV2']
    hdu1[0].header['INHERIT'] = hdu1[1].header['INHERIT']
    hdu1[0].header['EXTTYPE'] = hdu1[1].header['EXTTYPE']
#    hdu1[0].header['EXTNAME'] = hdu1[1].header['EXTNAME']
    hdu1[0].header['CRVAL1A'] = hdu1[1].header['CRVAL1A']
    hdu1[0].header['CRVAL2A'] = hdu1[1].header['CRVAL2A']
    hdu1[0].header['CRPIX1A'] = hdu1[1].header['CRPIX1A']
    hdu1[0].header['CRPIX2A'] = hdu1[1].header['CRPIX2A']
    hdu1[0].header['CTYPE1A'] = hdu1[1].header['CTYPE1A']
    hdu1[0].header['CTYPE2A'] = hdu1[1].header['CTYPE2A']
    hdu1[0].header['CUNIT1A'] = hdu1[1].header['CUNIT1A']
    hdu1[0].header['CUNIT2A'] = hdu1[1].header['CUNIT2A']


#h1head = hdu1[0].header + hdu1[1].header
    h1head  = hdu1[0].header 
    hdunew  = fits.PrimaryHDU(scidata_bin, h1head)
    hdunew2 = fits.ImageHDU(maskdata_bin, h1head)
    hdul = fits.HDUList([hdunew,hdunew2]) 
    hdul.writeto(i.replace('.fits','_bin.fits'),overwrite = True)