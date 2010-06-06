#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("./../")
from modisficator.modis_db import pg_modis_db
import glob
import time

db = pg_modis_db ( )
#try:
    #db.create_db()
#except:
    #pass
files = glob.glob ("/data/geospatial_11/ucfajlg/MODIS/mod09/*.hdf")
files = files + glob.glob ("/scratch/ucfajlg/Mexico/TERRA/MOD09GA/h09v07/*.hdf")
files = files + glob.glob ("/data/geospatial_10/ucfajlg/MCD45_SAfrica/*.hdf")
files = files + glob.glob ("/data/geospatial_10/ucfajlg/MCD43A4_SAfrica/*.hdf")
files = files + glob.glob ("/data/geospatial_10/ucfajlg/MCD15A2_SAfrica/*.hdf")
files = files + glob.glob ("/data/geospatial_10/ucfajlg/MCD43A1/*.hdf")
files = files + glob.glob ("/data/geospatial_10/ucfajlg/MOD12/*.hdf")

files.sort()
for fich in files:
    if fich.find(".xml")<0:
        fname = fich.split("/")[-1].split(".")
        tile = fname[2]
        product = fname[0]
        if product.find("MOD")>=0:
            platform="TERRA"
        elif product.find("MYD")>=0:
            platform="AQUA"
        elif product.find("MCD")>=0:
            platform="COMBINED"
        print fname, product, platform
        timestamp = time.strftime( "%Y-%m-%d", \
                    time.strptime( fname[1], "A%Y%j" ))
        db.insert_record ( "TERRA", product, tile, timestamp, \
                fich, "NONE", fich+".xml" )
