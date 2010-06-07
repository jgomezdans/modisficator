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
        if num_fires > 0:
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
    x_pixels = .5
    y_pixels = .5
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

def do_tseries_plots ( chunk, af_date ):
    import datetime
    import pylab
    import numpy
    import pdb
    
    af_date = pylab.datestr2num ( datetime.datetime.strptime(af_date, \
                "A%Y%j").strftime("%Y-%m-%d") )
    dates_mcd43 = pylab.datestr2num([ \
        datetime.datetime.strptime(d, \
        "A%Y%j").strftime("%Y-%m-%d") \
        for d in chunk['dates'] ])
    pylab.subplot(211)
    rho_nir = chunk['Nadir_Reflectance_Band2']
    rho_qa = chunk ['BRDF_Albedo_Quality']
    rho_nir = numpy.where ( rho_qa <= 1, rho_nir, numpy.nan )
    rho_nir[rho_nir>1] = numpy.nan
    pdb.set_trace()
    [ pylab.plot_date ( dates_mcd43, \
        rho_nir[:, i], '-s', label="Pix %d" % (i+1) ) \
        for i in xrange(9) ]
    #pylab.axvline ( af_date )
    pylab.legend(loc='best')
    pylab.ylabel(r'NIR NBAR reflectance [-]')
    pylab.xlabel(r'Date' )
    pylab.grid(True)
    pylab.subplot(212)
    rho_swir = chunk['Nadir_Reflectance_Band5']
    rho_swir = numpy.where ( rho_qa <= 1, rho_swir, numpy.nan )
    rho_swir[rho_swir>1] = numpy.nan
    [ pylab.plot_date ( dates_mcd43, \
        rho_swir[:, i], '-s', label="Pix %d" % (i+1) ) \
        for i in xrange(9) ]
    pylab.legend(loc='best')
    #pylab.axvline ( af_date )
    pylab.ylabel(r'SWIR NBAR reflectance [-]')
    pylab.xlabel(r'Date' )
    pylab.grid(True)
    

def main ( tile, start_date, end_date ):
    from modisficator import get_modis_data
    import pylab
    import datetime
    import cPickle
    f = open("test/sample.pkl", 'w')
    for retval in get_modis_data( tile, "MOD14A1", \
                start_date, end_date=end_date):
        # Apparently, GDAL doesn't do unicode
        hdf_file = (retval[1]).encode( 'ascii' )
        afires = get_active_fires ( hdf_file )
        for dates in afires.iterkeys():
            for detection in afires[dates]:
                D = get_nbar_rho ( detection[0], \
                        detection[1],  dates )
                #pdb.set_trace()
                do_tseries_plots ( D, dates)
                cPickle.dump ( (D, dates), f )
                
                break
            break
        break
        f.close()
        
if __name__ == "__main__":
    main( "h19v10", "2004-08-25", "2004-09-05" )
