#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The MODIS products database. This code manages (creation and search)
a sqlite database that stores MODIS products that have been downloaded,
 with the path where the data are stored. Simple queries (by tile, dates,
 product type) are available.
"""
import sqlite3

class modis_db:
    """
    The modis_db class stores the MODIS products and is able to search
    them.
    """
    def __init__ ( self, db_location="/home/ucfajlg/python/" + \
                                     "modisficator/modis_db.sqlite" ):
        """
        The creator. Usually requires a loction for the db, which could
        be made unique per user (eg ~/Data/modis_db.sqlte or something)

        :parameter db_location: The location of the sqlite database
        """
        self.db_file = db_location
        self.connect_to_db ()
        

    def connect_to_db ( self ):
        """
        A method to connect to the database. Should test for exceptions?
        """
        self.db_conn = sqlite3.connect( self.db_file )

    def create_db ( self ):
        """
        If the database doesn't exist, create it.
        """
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
        """
        Insert records into database. If they are already there, we
        should fire an exception, so TODO!

        :parameter platform: AQUA, TERRA or COMBINED
        :parameter product: The product name, such as MOD09GA
        :parameter tile: The tile, such as h17v04.
        :parameter date: The MODIS product timestamp, in YYYY-MM-DD format
        :parameter data_file: Full path to HDF datafile
        :parameter browse_file: Full path to JPG brose image.
        :parameter metadata_file: Full path to XML metadata file.
        """
        c = self.db_conn.cursor()
        sql_code = """INSERT INTO modis_data values ( '%s','%s','%s', \
                     '%s','%s','%s','%s')""" % ( platform, product, \
                            tile, date,  data_file, \
                            browse_file, metadata_file )
        c.execute ( sql_code )
        
        self.db_conn.commit()
        c.close()
        
    def find_start_date ( self, product ):
        """
        Find the starting date of data in the MODIS FTP server
        """
        c = self.db_conn.cursor()
        sql_code = "SELECT start_date, periodicity FROM modis_ftp_vault WHERE product=%s;" % \
                    product
        c.execute ( sql_code )
        result = c.fetchall()
        return result
        
    def get_ftp_dir ( self, product ):
        """
        Get the location of the product in NASA's FTP server from DB
        """
        c = self.db_conn.cursor()
        sql_code = "SELECT product_dir, platform FROM modis_ftp_vault" + \
                " WHERE product=%s.%s;" % ( product, "005")
        c.execute ( sql_code )
        result = c.fetchall()
        return result[0]

        
    def find_data ( self, product=None, tile=None, \
                          date_start=None, date_end=None, timestamp=None ):
        """
        Finding granules. Search the database for granules, builds an
        SQL query and returns the rows or an empty list if none are found.
        The temporal query allows searching for granules before a time,
        after a time, for a period, or for a given date only (timestamp
        option).

        :parameter product: Product name
        :parameter tile: tile
        :parameter date_start: Starting date (inclusive)
        :parameter date_end: Ending date (inclusive)
        :parameter timestamp: Fish one particular date ONLY
        """
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
        if timestamp == None:
            if date_start != None:
                if iand:
                    sql_code += "AND date>=='%s' " % date_start
                else:
                    sql_code += "WHERE date>='%s' "% date_start
                    iand = True
            if date_end != None:
                if iand:
                    sql_code += "AND date<='%s' " % date_end
                else:
                    sql_code += "WHERE date<='%s' "% date_end
                    iand = True
        else:
            if (date_start != None) or (date_end != None):
                raise ValueError, "Either a timestamp or a period are admissible"
            else:
                if iand:
                    sql_code += "AND date='%s' " % timestamp
                else:
                    sql_code += "WHERE date='%s' "% timestamp
                    iand = True

        
        c.execute (sql_code )
        result = c.fetchall()
        return result

class pg_modis_db ( modis_db ):
    import psycopg2
    """
    The modis_db class stores the MODIS products and is able to search
    them. POSTGRESQL version
    """
    def __init__ ( self, user="fire", host="oleiros.geog.ucl.ac.uk", \
                    password="fire" ):
        """
        The creator. Usually requires a loction for the db, which could
        be made unique per user (eg ~/Data/modis_db.sqlte or something)
        
        :parameter db_location: The location of the sqlite database
        """
        dbname = "modis_vault"
        dsn = "dbname='%s' user='%s' host='%s' password='%s' port='5433'" \
            % ( dbname, user, host, password )
        self.connect_to_db (dsn )

    def connect_to_db ( self, dsn ):
        """
        A method to connect to the database. Should test for exceptions?
        """
        try:
            self.db_conn = psycopg2.connect( dsn )
        except:
            print "Can't connect to database. Sorry!"


