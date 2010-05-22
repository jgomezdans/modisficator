# -*- coding: utf-8 -*-
from nose.tools import *
from modisficator.modis_db import *

def test_create_class():
    m = modis_db()

#def test_connect_to_db ():
    #m = modis_db()
    #m.create_db()

def test_insert_record():
    m = modis_db()
    m.insert_record ( "TERRA", "MOD09GA.005", "h19v10", "2004.05.18", "/tmp/this.dat", "/tmp/that.dat", "/tmp/stuff.dat")