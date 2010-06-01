#!/usr/bin/env python
# -*- coding: utf-8 -*-


from modis_db import *
from downloader import *

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