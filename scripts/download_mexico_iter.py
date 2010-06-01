#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("./../")
###from modisficator.downloader import downloader


###d = downloader( "h09v07" )

###output_files = d.get_product( "MOD09GA", "2003.03.01", "TERRA", end_date="2003.03.05")
from modisficator import get_modis_product


for retval in get_modis_product( "h09v07", "MOD09GA","2003.03.01", "TERRA",end_date="2003.03.08" ):
    print retval
