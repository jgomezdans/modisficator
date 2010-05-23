#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

class modis_db:
    def __init__ ( self, db_location="/home/ucfajlg/python/" + \
                                     "modisficator/modis_db.sqlite" ):
        self.db_file = db_location
        self.connect_to_db ()
        print self.db_file

    def connect_to_db ( self ):
        self.db_conn = sqlite3.connect( self.db_file )

    def create_db ( self ):
        c = self.db_conn.cursor()
        
        sql_code = '''CREATE TABLE modis_data
                (platform TEXT,
                product TEXT, tile TEXT, date TEXT,
                data_file TEXT, browse_file TEXT,
                metadata_file TEXT,PRIMARY KEY (product, tile, date ))'''
        c.execute ( sql_code )
        self.db_conn.commit()
        c.close()

    def insert_record ( self, platform, product, tile, date, \
                data_file, browse_file, metadata_file ):

        c = self.db_conn.cursor()
        sql_code = """INSERT INTO modis_data values ( '%s','%s','%s', \
                     '%s','%s','%s','%s')""" % ( platform, product, \
                            tile, date,  data_file, \
                            browse_file, metadata_file )
        c.execute ( sql_code )
        print sql_code
        self.db_conn.commit()
        c.close()

    def find_data ( self, product=None, tile=None, \
                          date_start=None, date_end=None ):
        c = self.db_conn.cursor()
        sql_code = """SELECT * FROM modis_data """
        iand = False
        if product != None:
            sql_code += "WHERE product='%s' " % product
            iand = True
        if tile != None:
            if iand:
                sql_code += "AND tile='%s' " % tile
            else:
                sql_code += "WHERE tile='%s' "% tile
                iand = True
        if date_start != None:
            if iand:
                sql_code += "AND date>=='%s' " % date_start
            else:
                sql_code =+ "WHERE date>='%s' "% date_start
                iand = True
        if date_end != None:
            if iand:
                sql_code =+ "AND date<='%s' " % date_end
            else:
                sql_code =+ "WHERE date<='%s' "% date_end
                iand = True
        print sql_code
        c.execute (sql_code )
        result = c.fetchall()
        return result