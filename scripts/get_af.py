# -*- coding: utf-8 -*-
"""
    Stuff about getting things from the web
"""
from modisficator import wsdl_modis


def get_active_fires ( fname, fire_thresh=8 ):
    """
    Get active fires from MOD14A1.005 dataset. Returns a list of longitudes, latitudes, and day of fire
    """
    from osgeo import gdal
    from osgeo import osr
    import datetime
    import numpy

    fnameout = fname.replace(".hdf", "_LonLat.txt")
    fout = open ( fnameout, 'w' )
    gdaldataset = gdal.Open( 'HDF4_EOS:EOS_GRID:"%s":' % fname + \
                    'MODIS_Grid_Daily_Fire:FireMask' )
    start_date = gdaldataset.GetMetadata()['StartDate']
    start_date = datetime.datetime.strptime ( start_date, "%Y-%m-%d" )
    fires = gdaldataset.ReadAsArray()
    geo_transform = gdaldataset.GetGeoTransform()
    modis_srs = osr.SpatialReference()
    wgs84_srs = osr.SpatialReference()
    modis_srs.ImportFromWkt ( gdaldataset.GetProjectionRef() )
    wgs84_srs.ImportFromEPSG( 4326 )
    transform = osr.CoordinateTransformation( modis_srs, wgs84_srs )
    return_struct = {}
    for day in xrange(8):
    
        current_date = (start_date + \
                    datetime.timedelta(days = day)).strftime("A%Y%j")
        current_date_pretty = (start_date + \
                    datetime.timedelta(days = day)).strftime("%Y.%m.%d")
        ( y, x ) = numpy.nonzero ( fires[day, :, :] >= fire_thresh )
        num_fires = x.shape[0]
        sample_xy = [ gdal.ApplyGeoTransform ( geo_transform, \
                float( x[i] ), \
                float( y[i] ) ) \
                for i in xrange(x.shape[0]) ]
        sample_xy = numpy.array ( sample_xy )
        lonlat = transform.TransformPoints  ( sample_xy )
        lonlat = numpy.array(lonlat)[ :, :2 ]
        txt_out = ''.join ( ["%s ; %s ; %f ; %f\n"%( current_date_pretty, \
                  current_date, lonlat[i, 0], lonlat[i, 1]) \
                  for i in xrange( num_fires ) ] )
        return_struct [ current_date ] = lonlat
        fout.write ( txt_out )
    fout.close()
    return return_struct




def get_nbar_rho ( lon, lat, date, t_window = 42 ):
    """
    Get a time series of NBAR reflecances from the MODIS webservice
    """
    year = int(date[1:5])
    doy =  int(date[5:])
    return_dict = {}
    day_start = doy - t_window
    day_end = doy + t_window
    x_pixels = 0
    y_pixels = 0
    # First, get QA from MCD43A2 product
    product = "MCD43A2"
    for layer in ["BRDF_Albedo_Quality", "BRDF_Albedo_Band_Quality" ] :
        print layer
        ( dates, datas ) = wsdl_modis.wsdl_get_snapshot( lon, lat, \
                product, layer, year, \
                day_start, day_end, x_pixels, y_pixels )
        return_dict[ layer ] = datas
    # Now, NBAR refl from MCD43A4 product
    product = "MCD43A4"
    for nlayer in xrange(1, 8):
        layer = "Nadir_Reflectance_Band%d" % nlayer
        print layer
        ( dates, datas ) = wsdl_modis.wsdl_get_snapshot( lon, lat, \
                product, layer, year, \
                day_start, day_end, x_pixels, y_pixels )
        return_dict[ layer ] = datas
    return_dict[ 'dates' ] = dates
    return return_dict
    
if __name__ == "__main__":
    import pylab, numpy, time
    #queimas = get_active_fires ( \
        #"./test/MOD14A1.A2003137.h09v07.005.2007319180038.hdf" )
    dates = []
    queimas = numpy.loadtxt ( "./test/MOD14A1.A2003137.h09v07.005.2007319180038_LonLat.txt", \
        delimiter=";", usecols=(1,2,3), converters={1: dates.append})[:, 1:]
    ( lon, lat ) = queimas[200]
    date = dates[200].lstrip().rstrip()
    print "Starting slurrrping", time.asctime()
    datos = get_nbar_rho ( lon, lat, date, t_window = 42 )
    print "Finished slurrrping", time.asctime()