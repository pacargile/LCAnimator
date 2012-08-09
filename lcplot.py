#!/usr/bin/python
#
#    create phased LC plots for a LC animation
#
# Joshua Pepper 
# editted by Phill Cargile to fit in LCAnimator
#--------------------------------------------------------------------------

try:
    import numpy as np
except ImportError:
    raise Exception("numpy module needed for LC Plotter")

try:
    import matplotlib
    matplotlib.use('GTKAgg')
    import matplotlib.pyplot as plt
    plt.ioff()
except ImportError:
    raise Exception("matplotlib module needed for LC Plotter")

try:
    import cStringIO
except ImportError:
    raise Exception("cStringIO module needed for LC Plotter")


def makelc(JD,mag,Period,Tc,nBins,q,top,bot,ecflg=False):

   # define number of points in LC
   pts = len(JD)

   # define x-center point of plot
   Pc = 0.5
   
   # Turn JD into Phase
   JDp = np.array([x - (Tc + Pc*Period) for x in JD],dtype=np.float64)
   phase = np.array([(x / Period) - np.floor(x / Period) for x in JDp],dtype=np.float64)

   # Compute binned median of LC:
   BinWidth = 1.0 / nBins
   PhaseLoop = np.arange(nBins) 
   PhaseBins = np.array([(1.0 * x / nBins) + (BinWidth / 2.0) for x in PhaseLoop],dtype=np.float64)

   BinMedians = np.zeros(PhaseLoop.size)   
   BinCount   = np.zeros(BinMedians.size)
   WhichBin   = np.floor(nBins * phase)    
   for sbin in PhaseLoop:
      select  = (WhichBin == sbin)
      BinMags = mag[select]
      BinCount[sbin] = select.sum()
      if (BinCount[sbin] > 0):
         BinMedians[sbin] = np.median(BinMags)  
   BinMedians[(BinCount <= 0)] = None

   # Prepare figure object:

   x_low = -0.025
   x_high = 1.025

   fgcolor = 'white'
   bgcolor= 'black'

   fig = plt.figure(1,figsize=(8, 4.5), dpi=100)
   fig.clf()
   fig.subplots_adjust(left=0.15, right=0.96, bottom=0.15, top=0.84)
   ax1 = fig.add_subplot(111,axisbg=bgcolor)  
   ax1.grid(False)

   # format tick marks
   for ax in [ax1.xaxis, ax1.yaxis]:
      [t.set_markersize(10) for t in ax.get_ticklines(minor=False)] 
      for yn in [True,False]:      
         [t.set_color(fgcolor) for t in ax.get_ticklines(minor=yn)]
   tickfmt = plt.ScalarFormatter(useOffset=False) 
   ax1.yaxis.set_major_formatter(tickfmt)        

   # format binned point size
   medmsize = 4.5 + 1.5*pts/len(phase)
   
   # format data point size
   datasize = 1.5

   if (ecflg==True):
      # define transit points
      T1 = Pc - q/2
      T2 = Pc + q/2
   
      # Mark beginning and end of transit with vertical dashed lines):
      ax1.axvline(T1,lw=1,ls='--',color='cyan') ; ax1.axvline(T1+1,lw=1,ls='--',color='cyan')
      ax1.axvline(T2,lw=1,ls='--',color='cyan') ; ax1.axvline(T2+1,lw=1,ls='--',color='cyan')

   # create strings for text on plot
   etime = int(JD[-1] - JD[0])
   timetext = "observed across %d days " % etime
   ptstext = "%d observations" % pts

   # plot data and bins
   ax1.plot(phase, mag, 'wo', ms=datasize)
   ax1.plot(PhaseBins, BinMedians, 'rs', ms=medmsize)

   # set plot axis
   ax1.set_xlim(x_low,x_high)
   ax1.set_ylim(bot, top)      
   ax1.set_xlabel("Phase", fontsize=15)    
   ax1.set_ylabel("Star Brightness", fontsize=15)

   # put text on plot
   ax1.text(0, -0.0225, ptstext, fontsize=15, color='black')
   ax1.text(0.55, -0.0225, timetext, fontsize=14, color='black')

   # write JPG string and return it

   # create a StingIO to stick fake figure in
   output = cStringIO.StringIO()
   fig.savefig(output,format='jpg')
   
   # read the JPG output as a string called contents
   contents = output.getvalue()
   output.close()
   
   return contents
