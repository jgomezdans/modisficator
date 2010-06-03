# -*- coding: utf-8 -*-
from mpl_toolkits.basemap import Basemap
import pylab
import numpy

queimas = numpy.loadtxt ( "./test/MOD14A1.A2003137.h09v07.005.2007319180038_LonLat.txt", delimiter=";", usecols=(2,3))

projection_opts={'projection':'cyl','resolution':'c'}
m = Basemap(  urcrnrlon=queimas[:,0].max() + 0.5, \
    urcrnrlat=queimas[:, 1].max() + 0.5, \
    llcrnrlon=queimas[:, 0].min() - 0.5, \
    llcrnrlat=queimas[:, 1].min() - 0.5, ** projection_opts )
#m.drawcoastlines (linewidth=0.5, color='k')
m.drawcountries(linewidth=1, color='w')
m.bluemarble()

m.plot ( queimas[:,0], queimas[:,1], 'sr' )
#m.drawmapboundary()
pylab.show()