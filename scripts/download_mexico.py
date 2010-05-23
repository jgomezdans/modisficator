#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("./../")
from modisficator.downloader import downloader


d = downloader( "h09v07" )

output_files = d.get_product( "MOD09GA", "2003.03.01", "TERRA", end_date="2003.06.30")
