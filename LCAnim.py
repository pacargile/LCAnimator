#! /usr/bin/env python
##########################################################################
#
#     Light Curve Animator
#
##########################################################################
#  
#  Software that takes a light curve file and creates a phase animation.
#
#  Requires:
#
#      Python 2.7  (only tested on Python 2.7)
#      Python modules: subprocess, cStringIO, numpy, matplotlib, atpy
#      Python's MatPlotLib requires GTKAgg backend to output JPEG
#      FFmpeg (used to create movie)
#      FFmpeg codec modules: 
#             MJPEG (to read in JPEGs), libx264 (to output MP4 movie)
#
##########################################################################

# import modules smartly
import sys, os, time

try:
    import subprocess
except ImportError:
    raise Exception("subprocess module needed for LC Animator")

try:
    import numpy as np
except ImportError:
    raise Exception("numpy module needed for LC Animator")

try:
    import re
except ImportError:
    raise Exception("re module needed for LC Animator")

try:
    import atpy
except ImportError:
    raise Exception("ATPy module needed for LC Animator")

try:
    import lcplot
except ImportError:
    raise Exception("Uses the lcplot software to create the figures")

##########################################################################

# Define the makemovie class with the nessesary functions

class MakeMovie(object):
    
    def __init__(self,size,filename="output.mp4",rate=20):
        ''' 
        
        Takes a series of JPEG images that have been broadcast to the StdIn
        and converts them into a mp4 movie using ffmpeg
        
        '''

        self.size = size

        cmdstring = ('ffmpeg',
                     '-loglevel','panic',
                     '-vstats_file','templog',
                     '-f','image2pipe',
                     '-vcodec', 'mjpeg',
                     '-r', '{0}/1'.format(rate),
                     '-s', '{0}x{1}'.format(size[0],size[1]),
                     '-i', 'pipe:',
                     '-y',
                     '-vcodec', 'libx264',
                     '-threads','0',
                     '-f','mp4',
                     '-subq','5',
                     filename)

        self.p = subprocess.Popen(cmdstring, 
                                  stdin=subprocess.PIPE,
                                  shell=False)

    def run(self,image):
        '''

        write image to StdIn
        
        '''
        self.p.stdin.write(image)
        
    def close(self):
        ''' 
        
        close StdIn

        '''
        self.p.stdin.close()

if __name__ == "__main__" :
    starttime = time.time()
    # define frame rate, output filename, deminsions of movie
    rate = 20
    outf = 'test_new.mp4'
    W,H = 800,450

    # define the MakeMovie Class

    video = MakeMovie((W,H),outf,rate=rate)

    # read in LC
    
    inputLC = atpy.Table('comb_sd.dat',type='ascii')
    
    # calculate median mag
    
    medmag = np.median(inputLC.mag)
    inputLC.mag = inputLC.mag - medmag
    
    # define the specifics of LC
    per = 4.113791
    Tc = 5974.60356
    nBins = 50
    q = 0.04

    # define vertical plotting bounds
    top = min(inputLC.mag)   
    bot = max(inputLC.mag)   
    buf = (bot - top) / 15.0  
    top -= buf                
    bot += buf                

    # define median mag of full LC
    medmag = np.median(inputLC.mag)

    # Define sampling of the LC curve
    
    # linear sampling
    indf = np.linspace(1,len(inputLC.MJD),1000)

    # make sampling integers
    inds = np.rint(indf)

    # use for loop to create frames and write them into StdIn for FFMpeg
    startofloop = time.time()
    for ii in inds:
        sys.stdout.write('  processing '+str(ii)+'/'+str(len(inputLC.MJD))+' datapoints\r')
        
        # run the lcplot.makelc function and return the figure object
        contents = lcplot.makelc(inputLC.MJD[:ii],inputLC.mag[:ii],per,Tc,nBins,q,top,bot,ecflg=False)
        
        # write JPG string to StdIn for FFMpeg
        video.run(contents)            
        
        # on last frame include vertical lines and repeat for x seconds
        
        if ii == len(inputLC.MJD):
            # calculate number of needed additional frames
            addtime = 2.5
            x = np.array(np.rint(rate*addtime),dtype=np.uint8)
            
            print ''
            for jj in range(x):
                sys.stdout.flush()
                sys.stdout.write('  writing '+str(jj)+'/'+str(x)+' final frames\r')
                        
                # run makelc with ecflg=True
                contents = lcplot.makelc(inputLC.MJD[:ii],inputLC.mag[:ii],per,Tc,nBins,q,top,bot,ecflg=True)
                
                # write additional JPG string to StdIn for FFMpeg
                video.run(contents)            

        # flush the stdout so that it updates status
        sys.stdout.flush()

    # Close the video object
    print ''
    video.close()

    endtime = time.time()

    print 'total time taken', (endtime -  starttime)/60.0, 'min'
    print 'to start of loop', (endtime - startofloop)/60.0, 'min'
    
