#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("./../")
from modisficator.modis_db import modis_db
import glob
import time

db = modis_db ( db_location="/home/ucfajlg/Data/scratch/modis_db.sqlite" )
try:
    db.create_db()
except:
    pass
files = glob.glob ("/data/geospatial_11/ucfajlg/MODIS/mod09/*.hdf")
files = files + glob.glob ("/scratch/ucfajlg/Mexico/TERRA/MOD09GA/h09v07/*.hdf")
files.sort()
for fich in files:
    if fich.find(".xml")<0:
        fname = fich.split("/")[-1].split(".")
        tile = fname[2]
        timestamp = time.strftime( "%Y-%m-%d", \
                    time.strptime( fname[1], "A%Y%j" ))
        db.insert_record ( "TERRA", "MOD09GA", tile, timestamp, \
                fich, "NONE", fich+".xml" )
