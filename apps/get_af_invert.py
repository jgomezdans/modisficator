#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SYNOPSIS

get_af_invert.py [-h,--help] [-v,--verbose] [--version]

DESCRIPTION

This script downloads the MODIS TERRA active fire product (MOD14A1)
for a given tile and temporal period, locates the active fires, and
outputs them to a text file indicating the date, longitude and
latitude. Each of these samples is then used to query the MODIS webservice
to download a time series of NBAR reflectances (+ associated QA flags). The
dates closest to the fire (pre- and post) are selected on terms of QA flags, and
used to invert a fire model. The results of this inversion are stored, and so
is the pre- and post-fire reflectance data.

EXAMPLES

get_af_invert.py --tile h19v10 --start 2004-05-01 --end 2004-09-31


AUTHOR

Jose Gomez-Dans <j.gomez-dans@geog.ucl.ac.uk>

LICENSE

This script is in the public domain, free from copyrights or restrictions.

VERSION

1.0
"""
import sys
sys.path.append("/home/ucfajlg/Data/python/modisficator")

from modisficator import wsdl_modis, fire_inverter
import sys
import os
import traceback
import optparse

CONTADOR = 0

def get_active_fires ( fname, fire_thresh=8 ):
    """
    Get active fires from MOD14A1.005 dataset. Returns a list of longitudes, latitudes, and day of fire
    """
    from osgeo import gdal
    from osgeo import osr
    import datetime
    import numpy
    import pdb

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
            txt_out = ''.join ( ["%s ; %s ; %f ; %f ; %d ; %d\n"%( current_date_pretty, \
                    current_date, lonlat[i, 0], lonlat[i, 1], x, y) \
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
        ( dates, datas ) = wsdl_modis.wsdl_get_snapshot( lon, lat, \
                product, layer, year, \
                day_start, day_end, x_pixels, y_pixels )
        return_dict[ layer ] = datas
    # Now, NBAR refl from MCD43A4 product
    product = "MCD43A4"
    for nlayer in xrange(1, 8):
        layer = "Nadir_Reflectance_Band%d" % nlayer
        
        ( dates, datas ) = wsdl_modis.wsdl_get_snapshot( lon, lat, \
                product, layer, year, \
                day_start, day_end, x_pixels, y_pixels )
        return_dict[ layer ] = datas
    return_dict[ 'dates' ] = dates
    return return_dict

def do_tseries_plots ( chunk, af_date, num_pixels=9 ):
    """
    Do plots of NBAR reflectance before and after the event.
    """
    import datetime
    import numpy
    import pdb
    import pylab
    af_date = pylab.datestr2num ( datetime.datetime.strptime(af_date, \
                "A%Y%j").strftime("%Y-%m-%d") )
    dates_mcd43 = pylab.datestr2num([ \
        datetime.datetime.strptime(d, \
        "A%Y%j").strftime("%Y-%m-%d") \
        for d in chunk['dates'] ])

    passer = chunk['BRDF_Albedo_Quality']
    rho = numpy.zeros ( (7, chunk['Nadir_Reflectance_Band1'].shape[0], \
            chunk['Nadir_Reflectance_Band1'].shape[1]))
    rho[0, : :] = numpy.where ( numpy.logical_and (passer<=1, \
        chunk['Nadir_Reflectance_Band1']<1.), \
        chunk['Nadir_Reflectance_Band1'], numpy.nan )

    rho[1, : :] = numpy.where ( numpy.logical_and (passer<=1, \
        chunk['Nadir_Reflectance_Band2']<1.), \
        chunk['Nadir_Reflectance_Band2'], numpy.nan )

    rho[2, : :] = numpy.where ( numpy.logical_and (passer<=1, \
        chunk['Nadir_Reflectance_Band3']<1.), \
        chunk['Nadir_Reflectance_Band3'], numpy.nan )

    rho[3, : :] = numpy.where ( numpy.logical_and (passer<=1, \
        chunk['Nadir_Reflectance_Band4']<1.), \
        chunk['Nadir_Reflectance_Band4'], numpy.nan )

    rho[4, : :] = numpy.where ( numpy.logical_and (passer<=1, \
        chunk['Nadir_Reflectance_Band5']<1.), \
        chunk['Nadir_Reflectance_Band5'], numpy.nan )

    rho[5, : :] = numpy.where ( numpy.logical_and (passer<=1, \
        chunk['Nadir_Reflectance_Band6']<1.), \
        chunk['Nadir_Reflectance_Band6'], numpy.nan )

    rho[6, : :] = numpy.where ( numpy.logical_and (passer<=1, \
        chunk['Nadir_Reflectance_Band7']<1.), \
        chunk['Nadir_Reflectance_Band7'], numpy.nan )

    wavelengths = numpy.array([645., 858.5, 469., 555., \
                    1240., 1640., 2130.])

    tdiff = (af_date - dates_mcd43)
    post_sel = (af_date - dates_mcd43) <= 0
    pre_sel = (af_date - dates_mcd43) > 0
    rho_pre = numpy.zeros ( (num_pixels, 7) )
    rho_post = numpy.zeros ( (num_pixels, 7) )
    fcc_arr = numpy.zeros ( num_pixels )
    a0_arr = numpy.zeros ( num_pixels )
    a1_arr = numpy.zeros ( num_pixels )
    a2_arr = numpy.zeros ( num_pixels )
    for pxl in xrange ( num_pixels ):
        for band in xrange (0, 7):
            for tsample in xrange ( pre_sel.shape[0] ):
                tdiff[tsample]
                if  pre_sel[tsample] and \
                    (numpy.isfinite ( rho[ band, tsample, pxl ] )):
                    rho_pre[ pxl, band] = rho[ band, tsample, pxl ]

            #pdb.set_trace()
            for tsample in xrange ( post_sel.shape[0]-1, -1, -1 ):
                #pdb.set_trace()
                if (post_sel[tsample]) and \
                            numpy.isfinite ( rho[ band, tsample, pxl ] ):
                    rho_post[ pxl, band] = rho[ band, tsample, pxl ]

 
        ( fcc, a0, a1, a2, sBurn, sFWD, rmse,fccUnc, a0Unc, a1Unc, a2Unc ) = \
            fire_inverter.InvertSpectralMixtureModel (  rho_pre[pxl,:], \
            rho_post[pxl,:], wavelengths )
        fcc_arr[ pxl ] = fcc
        a0_arr [ pxl ] = a0
        a1_arr [ pxl ] = a1
        a2_arr [ pxl ] = a2
    # Select a single pixel based on some heuristics
    winner = -1
    fcc_max = 0.
    for pxl in xrange( num_pixels ):
        
        if (fcc_arr[ pxl ] > fcc_max) :
                fcc_max = fcc_arr [ pxl ]
                winner = pxl
    if winner == -1:
        return None # No suitable fires returned
    else:
        store_file = save_inversion ( fcc_arr[pxl], a0_arr[pxl], a1_arr[pxl], \
            a2_arr[pxl], \
            rho_pre[pxl, :], rho_post[pxl, :], wavelengths )
        return ( fcc_arr[pxl], a0_arr[pxl], a1_arr[pxl], a2_arr[pxl], \
                store_file )

def save_inversion ( fcc, a0, a1, a2, rho_pre, rho_post, wv ):
    """
    Saves inversion results to a file, plus pre- and post-fire reflectance.
    """
    global CONTADOR
    global TILE
    global FECHA
    CONTADOR += 1
    fname = os.path.expanduser("~/Data") + \
                "/AF_inversions/%s/%s/%s_%s_%05d.txt"% ( TILE, FECHA, \
                        TILE, FECHA, CONTADOR )
    if os.path.exists ( os.path.expanduser("~/Data") + \
                "/AF_inversions/%s/%s/" % ( TILE, FECHA ) ):
        fp = open ( fname, 'w' )
    else:
        os.makedirs (  os.path.expanduser("~/Data") + \
                "/AF_inversions/%s/%s/" % ( TILE, FECHA ) )
        fp = open ( fname, 'w' )
    fp.write ("# fcc: %f, a0: %f, a1: %f, a2: %f\n"%(fcc, a0, a1, a2) )
    i = 0
    
    for (i, w) in enumerate( wv ):
        fp.write ( "%f ; %f ; %f \n" % ( w, rho_pre[i], rho_post[i] ) )
        i =+ 1
    fp.close()
    return fname

def main ( tile, start_date, end_date ):
    """
    Main function
    """
    from modisficator import get_modis_data
    import pylab
    import datetime
    
    if not os.path.exists(os.path.expanduser("~/Data/AF_inversions")):
        # Directory doesn't exist. Create it.
        os.mkdir ( os.path.expanduser("~/Data/AF_inversions") )
        print "Making dir %s" % os.path.expanduser("~/Data/AF_inversions")
        print "Stuff will be saved there"
    fname = os.path.expanduser("~/Data/AF_inversions") + \
            "/%s_%s_%s.dat" % ( tile, start_date, end_date)
    
    f = open( fname, 'w')
    MAX_NUM_FIRES_TILE = 100
    global TILE
    global FECHA
    TILE = tile
    for retval in get_modis_data( tile, "MOD14A1", \
                start_date, end_date=end_date):
        # Apparently, GDAL doesn't do unicode
        hdf_file = (retval[1]).encode( 'ascii' )
        print "Doing file", hdf_file
        sys.stdout.flush()
        afires = get_active_fires ( hdf_file )
        for dates in afires.iterkeys():
            print "Doing date", dates
            sys.stdout.flush()
            num_fires = 0
            for detection in afires[dates]:
                D = get_nbar_rho ( detection[0], \
                        detection[1],  dates )
                #pdb.set_trace()
                FECHA = dates
                
                retonno = do_tseries_plots ( D, dates)
                if retonno != None:
                    # An "optical fire" was detected
                    ( fcc, a0, a1, a2, store_file ) = retonno
                    f.write ( "%s ; %f ; %f ; %f ; %f ; %f ; %f ; %s\n" % ( \
                    dates, detection[0], detection[1], fcc, a0, a1, a2, \
                    store_file ) )
                    num_fires += 1
                    f.flush()
                if num_fires > MAX_NUM_FIRES_TILE:
                    break
            
        
    f.close()
        
if __name__ == "__main__":

    try:
        parser = optparse.OptionParser(formatter = \
            optparse.TitledHelpFormatter(), usage=globals()['__doc__'], \
            version='1.0')
        parser.add_option ( '-t', '--tile', action="store", dest="tile", \
                               help="Specify the tile (h19v10, for example)" )
        parser.add_option ( '-s', '--start', action="store", \
            dest="start_date", help="Start date in "+ \
                                "YYYY-MM-DD format." )
        parser.add_option( "-e", '--end', action="store", dest="end_date", \
                            help="End date in YYYY-MM-DD format" )

        if len(sys.argv) < 2:
            print "No options specified"
            print "Hence I'm doing southern Africa"
            
            for htile in xrange (19, 22):
                for vtile in xrange (9, 12):
                    tile = "h%02dv%02d" % ( htile, vtile )
                    print "Doing tile: ", tile
                    sys.stdout.flush()
                    for (start, end) in [ ("2004-05-25", "2004-06-05"),\
                            ("2004-07-25", "2004-08-05"), \
                            ("2004-08-25", "2004-09-05")]:
                        print "Doing period: %s-%s" % ( start, end )
                        sys.stdout.flush()
                        main( tile, start, end  )
                    

        (options, args) = parser.parse_args()
        main( options.tile, options.start_date, options.end_date )

    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(1)
            
