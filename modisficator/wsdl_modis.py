# -*- coding: utf-8 -*-
"""
A couple of useful functions to access the MODIS XML SOAP service.
"""
def wsdl_get_data_tseries ( lon, lat, product, layer, \
            year_start, year_end, x_pixels, y_pixels ):
    """
    Getting data from MODIS' WSDL server
    This function gets a time series of data, getting around
    the maximum of 10 allowed dates per query. It splits the
    query into chunks and returns arrays tranparently to the
    user.
    """
    from suds.client import Client
    import numpy
    import datetime

    WSDLFile = 'http://daac.ornl.gov/cgi-bin/MODIS/" + \
                "GLBVIZ_1_Glb_subset/MODIS_webservice.wsdl?WSDL'

    while True:
        try:
            #For some reason, I can't cache...
            client = Client( WSDLFile, cache=None ) 
            break
        except:
            print "Re-trying WSDL get..."

    date = []
    value = []
    tempo_out = []
    #QA_OK=numpy.array([0,1,8,32])
    for year in xrange(year_start, year_end+1):
        for day_start in numpy.arange(1, 365, 80):
            if (day_start+80) > 365:
                day_end = 365
            else:
                day_end = day_start+80
            #this is to get around the 80 day data limit

            ret = client.service.getsubset (lat, lon, product, layer, \
                    "A%4d%03d"%(year, day_start),"A%4d%03d"%(year, day_end), \
                    x_pixels, y_pixels)

            for time_step in xrange(len(ret.subset.item)):
                # Process time to get pylab-friendly time axis.
                tempo = ret.subset.item[time_step].strip().split(",")[2]
                tempo_out.append ( tempo )

                date.append( pylab.date2num( datetime.date( time.strptime(\
                    tempo,"A%Y%j")[0], time.strptime(tempo, "A%Y%j")[1], \
                    time.strptime(tempo, "A%Y%j")[2])) )
                # Extract QA vals...
                if layer == "sur_refl_day_of_year" or \
                   layer == "sur_refl_state_500m":
                    vals = numpy.array ( [int(f) for f in \
                        ret.subset.item[time_step].strip().split(",")[5:]])
                    value.append ( vals)
                else:
                    vals = numpy.array ( [float(f) for f in \
                        ret.subset.item[time_step].strip().split(",")[5:]])
                    value.append( vals*ret.scale)


    date = numpy.array ( date )
    value = numpy.array ( value )

    return ( date, value)

def wsdl_get_snapshot( lon, lat, product, layer, year, \
            day_start, day_end, x_pixels, y_pixels, date_format="MODIS" ):
    """
    Getting data from MODIS' WSDL server

    Similar to above, but not concentrated in getting X years, but rather a
    short interval in a year (i.e., pre- and post-disturbance data).
    """
    from suds.client import Client
    import numpy

    if date_format == "MODIS":
        def parse_date ( tempo ):
            """A function to return the MODIS date
            without parsing
            """
            return tempo
            
    elif date_format == "PRETTY":
        
        def parse_date ( tempo ):
            """
            Pretty printing the MODIS date
            """
            import datetime
            import time
            return datetime.date( time.strptime( \
                tempo, "A%Y%j")[0], time.strptime( tempo, "A%Y%j")[1], \
                time.strptime( tempo, "A%Y%j")[2] )
    elif date_format == "PYLAB":
        def parse_date ( tempo ):
            """
            Pylab uses  its own format for dates...
            """
            import datetime
            import time
            import pylab
            return pylab.date2num( datetime.date( time.strptime(\
                tempo, "A%Y%j")[0], time.strptime(tempo,"A%Y%j")[1], \
                time.strptime(tempo, "A%Y%j")[2]))
            
            
    WSDLFile = 'http://daac.ornl.gov/cgi-bin/MODIS/" +\
                "GLBVIZ_1_Glb_subset/MODIS_webservice.wsdl?WSDL'
    client = Client( WSDLFile, cache=None )
    #For some reason, I can't cache...
    #while True:
        #try:

            #break
        #except:
            #print "Re-trying WSDL get..."

    date = []
    value = []
    tempo_out = []
    #QA_OK=numpy.array([0,1,8,32])
    try:
        ret = client.service.getsubset (lat, lon, product, layer, \
            "A%4d%03d"%(year, day_start),"A%4d%03d"%(year, day_end), \
            x_pixels, y_pixels)
    except:
        raise ValueError, "Something wrong with your request. Time window?"

    for time_step in xrange(len(ret.subset.item)):
        # Process time to get pylab-friendly time axis.
        tempo = ret.subset.item[time_step].strip().split(",")[2]
        tempo_out.append ( tempo )

        date.append( parse_date ( tempo ) )
        
        if ret.scale == 0.:
            try:
                vals = numpy.array ( [int(f) for f in \
                    ret.subset.item[time_step].strip().split(",")[5:]])
            except ValueError:
                response = ret.subset.item[time_step].split("\n")[0] 
                vals = numpy.array ( [int(f) for f in \
                    response.strip().split(",")[5:]])
            value.append ( vals)
        else:
            try:
                vals = numpy.array ( [float(f) for f in \
                        ret.subset.item[time_step].strip().split(",")[5:]])
            except ValueError:
                response = ret.subset.item[time_step].split("\n")[0] 
                vals = numpy.array ( [int(f) for f in \
                        response.strip().split(",")[5:]])
            value.append( vals*ret.scale)


    date = numpy.array ( date )
    value = numpy.array ( value )

    return ( date, value)


