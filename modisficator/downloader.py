#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ftplib
import time
import os
import pdb
import sys
"""The downloader code downloads MODIS datasets from NASA's website.
"""
class invalid_platform(Exception):
    print "The platform you selected is not TERRA, AQUA or COMBINED"

class invalid_product(Exception):
    print "The product you selected does not appear to exist."


class downloader:
    """
    A downloader class
    """
    def __init__ ( self, tile, output_dir="/scratch/ucfajlg/Mexico/", \
                    collection="005" ):
        """
        For some reason, I put something about the collection there, which is not
        yeat in the database.
        """
        self.ftp_host = "e4ftl01u.ecs.nasa.gov"
        self.ftp = ftplib.FTP ( self.ftp_host )
        #self.ftp.set_debuglevel(2)
        self.ftp.set_pasv( True )
        self.ftp.login()
        self.collection = collection
        self.tile = tile
        self.output_dir = output_dir
        
    def get_list ( self, product_name, start_date, platform, end_date=None ):
        self.platform = platform
        self.product = product_name
        try:
            (ftp_dir, get_dates ) = self.__navigate_ftp ( \
                            product_name, start_date, platform, \
                            end_date=end_date )
        except:
            raise ValueError, "Some error occurred in __navigate_ftp!"
        return ( ftp_dir, get_dates )
        
    def __navigate_ftp ( self, product_name, start_date, platform, \
                        end_date=None ):

        """
        This is the method traverses NASA's FTP directory, selecting what
        files to download, in terms of tile, start and end date.

        :parameter product_name: The product shortname, for example MOD09GA.
        :parameter start_date: The starting date (2001.05.18, for example).
        :parameter platform: Not really needed, but one of "TERRA", "AQUA"
                             or "COMBINED".
        :parameter end_date: Optional end date. Otherwise, all data older than
                             start_date is returned.
        """
        platform_dir = {"TERRA":"/MOLT/", "AQUA":"/MOLA/", \
                        "COMBINED":"/MOTA/"}

        if not platform_dir.has_key(platform):
            raise invalid_platform, "Your platform was %s"%platform
        # Parse the start date to match FTP dir structure
        parsed_start_date = time.strptime(start_date, "%Y.%m.%d" )
        if end_date != None:
            parsed_end_date = time.strptime( end_date, "%Y.%m.%d" )
        # Change dir to product directory
        try:
            self.ftp.cwd ("/%s/%s.%s/"%( platform_dir[platform], \
                            product_name, self.collection ))
        except ftplib.error_perm:
            raise invalid_product, "This product doesn't seem to exist?"
        ftp_dir = "/%s/%s.%s/"%( platform_dir[platform], \
                                product_name, self.collection )
        # Now, get all the available dates (they are subdirs, so need
        # to parse return string).
        dates = []
        def parse(line):
            if line[0] == 'd':
                dates.append(line.rpartition(' ')[2])

        self.ftp.dir( parse )
        dates.sort()
        # Dates are here now.
        # Discard dates prior to start_date parameter...
        Dates = [ time.strptime(d, "%Y.%m.%d") for d in dates ]
        try:
            istart = [ i for i in xrange(len(Dates)) \
                    if Dates[i] == parsed_start_date ][0]
        except:
            raise ValueError, "Wrong start date!"
            
        # Do the same if we have an end date
        if end_date != None:
            try:
                iend = [ i for i in xrange(len(Dates)) \
                    if (Dates[i]>=parsed_start_date)\
                        and ( Dates[i]<=parsed_end_date) ][-1]
                print iend
            except:
                raise ValueError, "Wrong end date!"
            get_dates = dates[istart:iend]
        else:
            get_dates = list ( dates[istart] )
        return ( ftp_dir, get_dates )

    def get_product ( self, product_name, start_date, platform, \
                        end_date=None):
        """
        This is the method that does the downloading of a prdouct
        """

        # First, navigate FTP tree and get products
    
        ( ftp_dir, get_dates ) = self.__navigate_ftp ( \
                            product_name, start_date, platform, \
                            end_date=end_date )
        #except:
            #raise ValueError, "Some error occurred in __navigate_ftp!"
        
        out_dir = os.path.join ( self.output_dir, platform, product_name, \
                                self.tile )
        if not os.path.exists ( out_dir ):
            os.makedirs ( out_dir )
        output_files = []
        for fecha in get_dates:
            # For each date, cd into that dir, and grab all files.
            try:
                self.ftp.cwd ( "%s/%s"%(ftp_dir, fecha) )
            except ftplib.error_perm:
                    continue
            fichs = []
            self.ftp.dir ( fichs.append )
            # Now, only consider the ones for the tile we want.
            grab0 = [ f for f in fichs if f.find( self.tile ) >= 0 ]
            for grab_file in grab0:
                fname = grab_file.split()[7]
                f_out = open( os.path.join ( out_dir, fname), 'w')
                output_files.append ( os.path.join ( out_dir, fname) )

                # Download the file a chunk at a time
                # Each chunk is sent to handleDownload
                # RETR is an FTP command

                #
                def handle_download(block):
                    f_out.write(block)
                    f_out.flush()

                self.ftp.retrbinary('RETR ' + fname, handle_download )

                f_out.close()

        return output_files

    def download_product ( self, ftp_dir, get_date):
        """
        This is the method that does the downloading of a prdouct
        """

        out_dir = os.path.join ( self.output_dir, self.platform, self.product, \
                                self.tile )
        if not os.path.exists ( out_dir ):
            os.makedirs ( out_dir )
        output_files = []
        
        # For each date, cd into that dir, and grab all files.
        try:
            self.ftp.cwd ( "%s/%s"%(ftp_dir, get_date) )
        except ftplib.error_perm:
            raise ValueError, "Can't change dir to %s/%s"%(ftp_dir, get_date)
        fichs = []
        self.ftp.dir ( fichs.append )
        # Now, only consider the ones for the tile we want.
        grab0 = [ f for f in fichs if f.find( self.tile ) >= 0 ]
        for grab_file in grab0:
            fname = grab_file.split()[7]
            f_out = open( os.path.join ( out_dir, fname), 'w')
            output_files.append ( os.path.join ( out_dir, fname) )

            # Download the file a chunk at a time
            # Each chunk is sent to handleDownload
            # RETR is an FTP command

            #
            def handle_download(block):
                f_out.write(block)
                f_out.flush()

            self.ftp.retrbinary('RETR ' + fname, handle_download )

            f_out.close()

        return output_files