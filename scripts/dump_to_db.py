#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("./../")
from modisficator.modis_db import modis_db
import glob
import time

db = modis_db ( db_location="/home/ucfajlg/Data/scratch/modis_db.sqlite" )
db.create_db()
files = glob.glob ("/data/geospatial_11/ucfajlg/MODIS/mod09/*.hdf")
files.sort()
for fich in files:
    if fich.find(".xml")<0:
        fname = fich.split("/")[-1].split(".")
        tile = fname[2]
        timestamp = time.strftime( "%Y-%m-%d", \
                    time.strptime( fname[1], "A%Y%j" ))
        db.insert_record ( "TERRA", "MOD09", tile, timestamp, \
                fich, "NONE", fich+".xml" )
