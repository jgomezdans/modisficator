# -*- coding: utf-8 -*-


def GetActiveFires ( fname, fire_thresh=8 ):
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

if __name__ == "__main__":
    queimas = GetActiveFires ( \
        "./test/MOD14A1.A2003137.h09v07.005.2007319180038.hdf" )
