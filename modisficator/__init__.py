#!/usr/bin/env python
# -*- coding: utf-8 -*-


from modis_db import *
from downloader import *
import logging
from StringIO import StringIO
import sys
import os
import datetime
import pdb

# Set up logging
logging.basicConfig ( \
    level = logging.DEBUG, \
    format = '%(asctime)s %(levelname)s %(message)s', \
    filename='/data/geospatial_12/users/%s/MODIS/log/logfile_%s.log' % \
    (os.environ['USER'], datetime.datetime.now().strftime("%Y%m%d-%H%M%S") ), \
    filemode = 'w' )

log = logging.getLogger ( 'main-log' )


def __get_interval ( start_date, end_date, product, db ):
    import datetime
    start_modis_data, product_period = db.find_start_date ( product )[0]
    start_date = datetime.datetime.strptime ( start_date, "%Y-%m-%d" )
    end_date = datetime.datetime.strptime ( end_date, "%Y-%m-%d" )
    periodicity = datetime.timedelta ( days = product_period )
    t0 = datetime.timedelta(days=0)
    time_cursor = datetime.datetime.strptime ( start_modis_data, "%Y-%m-%d" )
    log.debug ("Getting intervals")
    while True:
        
        if t0 <= ( start_date - time_cursor ) <= periodicity:
            start_grab = time_cursor
        elif (time_cursor>=start_date) and \
                (( time_cursor ) >= ( end_date + periodicity )):
            end_grab = time_cursor
            break
        if time_cursor.year == (time_cursor + periodicity).year:
            time_cursor = time_cursor + periodicity
        else:
            anho = (time_cursor + periodicity).year
            time_cursor = datetime.datetime.strptime ( "%d-01-01"%anho,\
                "%Y-%m-%d")
    log.debug ( "Start: %s. End: %s"%( start_grab, end_grab ) )
    return ( start_grab, end_grab, periodicity )

def get_modis_data ( tile, product, start_date, end_date=None ):
    """
    An iterator to return MODIS HDF datasets by tile, product and dates. In each iteration, the function returns a dictionary with the following elements:

    1. A date in datetime format (you can convert it to anything you want with ``ret_date.strftime("%Y-%m-%d")``)
    2. The location of the HDF file (full path). You can then open it with GDAL, but remember to convert it to ASCII first (otherwise, GDAL complains): ``retval[1]).encode( 'ascii' )``
    3. A quicklook 'BROWSE' file (or NONE, if none present).
    4. An XML metadata file.

    If the data is not available in the system, this function will go away and fetch it. The data will be downloaded to ``/data/geospatial_12/users/$USERNAME/MODIS``, and a logs directory is stored there to see how things are going.

    :parameter tile: The MODIS tile, usually something like "h19v10" or "h09v07". This is case dependent.
    :parameter product: Product abbreviated name, something like "MOD09GA", "MCD15A2". Again, case sensitive.
    :parameter start_date: Requested start date, in the format "YYYY-MM-DD".
    :parameter end_date: Requested end date, in the format "YYYY-MM-DD". If not set, only the start date is considered
    """
    # If no end_date specified, single date is assumed.
    log.info ( "Starting iterator!" )
    if end_date is None:
        end_date = start_date
    # Instantiate classess
    db = pg_modis_db ()
    net_modis = downloader( tile )
    # Calculate the interval of dates that are needed
    # Returns start and end date, and MODIS product periodicity
    (start_grab, end_grab, periodicity ) = __get_interval \
                            ( start_date, end_date, product, db )
    #Set current date to start of leech period.
    curr_date = start_grab
    #Get the remote location and platform name in case we
    #need to download data not yet present in the Db
    ftp_dir, platform = db.get_ftp_dir ( product )
    net_modis.platform = platform
    net_modis.product = product
    net_modis.tile = tile
    if product == "MCD45A1": # Monthly product....
        curr_date.replace(day=1)
    
    # Iterator loop
    while True:
        # If the date is equal to the end date, break out of the loop
        if curr_date > end_grab:
            return
        else:
            #check whether curr_date is in DB
            tstamp = curr_date.strftime("%Y-%m-%d")
            resp = db.find_data ( product=product, \
                                tile=tile, timestamp=tstamp )
            #Depending on the lenght of resp, we either have the data
            # or not
            if len( resp ) == 0:
                # No product, need to download it
                # Do the FTPing
                log.info ("File not present, needs downloading")
                #pdb.set_trace()
                output_files = net_modis.download_product ( \
                    ftp_dir, curr_date.strftime( "%Y.%m.%d" ) )
                #Downloaded files need to be sorted out
                if output_files is None:
                    # Some sort of problem with download. Yields a None
                    yield None
                browse_file = "N/A"
                metadata_file = "N/A"
                for fich in output_files:
                    print fich
                    if (fich.find("JPG")>=0) or (fich.find("jpg")>=0):
                        browse_file = fich
                    elif fich.find(".xml")>=0:
                        metadata_file = fich
                    else:
                        data_file = fich
                # Store the newly downloaded product in DB
                log.info ("Done with downloading")
                db.insert_record ( platform, product, tile, \
                    curr_date.strftime( "%Y-%m-%d" ), \
                    data_file, browse_file, metadata_file )
                #"return" files
                log.info("Download registered into DB")
                curr_date = curr_date + periodicity
                if product=="MCD45A1":
                    curr_date.replace( day=1 )
                    
                yield ( curr_date, data_file, browse_file, metadata_file )
            else:
                curr_date = curr_date + periodicity
                if product=="MCD45A1":
                    curr_date.replace( day=1 )
                    # Groan...
                yield ( resp[0] )

################def get_modis_product ( tile, product_name, start_date, platform, \
                        ################end_date=None ):
    ################import pdb
    ################m_db = modis_db (db_location="/home/ucfajlg/Data/scratch/modis_db.sqlite")
    ################net_modis = downloader( tile )
    
    ################(ftp_dir, get_dates) = net_modis.get_list (  product_name, start_date, \
                    ################platform, end_date=end_date )
    ################if type ( get_dates ) == str:
        ################get_dates = list ( get_dates )
        
    ################for date in get_dates:
        ################db_query = m_db.find_data ( product=product_name, tile=tile, \
                        ################timestamp=date.replace(".", "-") )
        ################if len ( db_query ) == 0:
            ################# The file is not present. Download
            #################net_modis.
            
            ################output_files = net_modis.download_product( ftp_dir, date )
            ################for fich in output_files:
                ################if (fich.find("JPG")>=0) or (fich.find("jpg")>=0):
                    ################browse_file = fich
                ################elif fich.find(".xml")>=0:
                    ################metadata_file = fich
                ################else:
                    ################data_file = fich
            ################m_db.insert_record ( platform, product_name, tile, \
                            ################date.replace(".", "-"), \
                            ################data_file, browse_file, metadata_file )
            ################yield ( date, data_file, browse_file, metadata_file )
        ################else:
            ################# File is present
            ################data_file = db_query[0][4]
            ################browse_file = db_query[0][5]
            ################metadata_file = db_query[0][6]
            ################yield ( date, data_file, browse_file, metadata_file )