#!/usr/bin/env python
# -*- coding: utf-8 -*-


from modis_db import *
from downloader import *


def __get_interval ( start_date, end_date, product ):
    import datetime
    start_modis_data, product_period = db.find_start_date ( product )
    start_date = datetime.datetime.strptime ( start_date, "%Y-%m-%d" )
    end_date = datetime.datetime.strptime ( end_date, "%Y-%m-%d" )
    periodicity = datetime.timedelta ( days = product_period )
    
    time_cursor = datetime.datetime.strptime ( start_modis_data, "%Y-%m-%d" )
    while True:
        if ( time_cursor + periodicity ) == start_date:
            start_grab = time_cursor
        elif ( time_cursor ) == ( end_date + periodicity ):
            end_grab = time_cursor
            break
        time_cursor = time_cursor + periodicity

    return ( start_grab, end_grab, periodicity )

def get_modis_data ( tile, product, start_date, end_date=None ):
    """
    An iterator to return MODIS HDF datasets by tile, product and dates.
    """
    # If no end_date specified, single date is assumed.
    if end_date is None:
        end_date = start_date
    # Instantiate classess
    db = modis_db (db_location="/home/ucfajlg/Data/scratch/modis_db.sqlite")
    net_modis = downloader( tile )
    # Calculate the interval of dates that are needed
    # Returns start and end date, and MODIS product periodicity
    (start_grab, end_grab, periodicity ) = __get_interval \
                            ( start_date, end_date, product )
    #Set current date to start of leech period.
    curr_date = start_grab
    #Get the remote location and platform name in case we
    #need to download data not yet present in the Db
    platform, ftp_dir = db.get_ftp_dir ( product )
    # Iterator loop
    while True:
        # If the date is equal to the end date, break out of the loop
        if curr_date > end_grab:
            return
        else:
            #check whether curr_date is in DB
            resp = db.find_data ( self, product=product, \
                                tile=tile, timestamp=tstamp )
            #Depending on the lenght of resp, we either have the data
            # or not
            if len( resp ) == 0:
                # No product, need to download it
                curr_ftp_dir = ftp_dir + "/%s"% \
                            (curr_date.strftime( "%Y.%m.%d" ) )
                # Do the FTPing
                output_files = net_modis.download_product ( \
                                curr_ftp_dir, curr_date )
                #Downloaded files need to be sorted out
                for fich in output_files:
                    if (fich.find("JPG")>=0) or (fich.find("jpg")>=0):
                        browse_file = fich
                    elif fich.find(".xml")>=0:
                        metadata_file = fich
                    else:
                        data_file = fich
                # Store the newly downloaded product in DB
                db.insert_record ( platform, product, tile, \
                    date.replace(".", "-"), \
                    data_file, browse_file, metadata_file )
                #"return" files
                curr_date = curr_date + periodicity
                yield ( date, data_file, browse_file, metadata_file )
            else:
                curr_date = curr_date + periodicity
                yield ( resp[0] )

def get_modis_product ( tile, product_name, start_date, platform, \
                        end_date=None ):
    import pdb
    m_db = modis_db (db_location="/home/ucfajlg/Data/scratch/modis_db.sqlite")
    net_modis = downloader( tile )
    
    (ftp_dir, get_dates) = net_modis.get_list (  product_name, start_date, \
                    platform, end_date=end_date )
    if type ( get_dates ) == str:
        get_dates = list ( get_dates )
        
    for date in get_dates:
        db_query = m_db.find_data ( product=product_name, tile=tile, \
                        timestamp=date.replace(".", "-") )
        if len ( db_query ) == 0:
            # The file is not present. Download
            #net_modis.
            
            output_files = net_modis.download_product( ftp_dir, date )
            for fich in output_files:
                if (fich.find("JPG")>=0) or (fich.find("jpg")>=0):
                    browse_file = fich
                elif fich.find(".xml")>=0:
                    metadata_file = fich
                else:
                    data_file = fich
            m_db.insert_record ( platform, product_name, tile, \
                            date.replace(".", "-"), \
                            data_file, browse_file, metadata_file )
            yield ( date, data_file, browse_file, metadata_file )
        else:
            # File is present
            data_file = db_query[0][4]
            browse_file = db_query[0][5]
            metadata_file = db_query[0][6]
            yield ( date, data_file, browse_file, metadata_file )