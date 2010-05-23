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
        self.ftp.set_debuglevel(2)
        self.ftp.set_pasv( True )
        self.ftp.login()
        self.collection = collection
        self.tile = tile
        self.output_dir = output_dir

    def get_product ( self, product_name, start_date, platform, \
                        end_date=None):
        """
        This is the method that does the downloading of a prdouct
        """
        platform_dir = {"TERRA":"/MOLT/", "AQUA":"/MOLA/", \
                    "COMBINED":"/MOTA/"}
        
        if not platform_dir.has_key(platform):
            raise invalid_platform, "Your platform was %s"%platform
        parsed_start_date = time.strptime(start_date, "%Y.%m.%d" )
        if end_date != None:
            parsed_end_date = time.strptime( end_date, "%Y.%m.%d" )
        try:
            self.ftp.cwd ("/%s/%s.%s/"%( platform_dir[platform], \
                            product_name, self.collection ))
        except ftplib.error_perm:
            raise invalid_product, "This product doesn't seem to exist?"
        dates = []
        def parse(line):
            if line[0] == 'd':
                dates.append(line.rpartition(' ')[2])

        self.ftp.dir( parse )
        dates.sort()

        
        Dates = [ time.strptime(d, "%Y.%m.%d") for d in dates ]
        try:
            istart = [ i for i in xrange(len(Dates)) \
                    if Dates[i] == parsed_start_date ][0]
            print istart
        except:
            raise ValueError, "Wrong start date!"
        
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
        out_dir = os.path.join ( self.output_dir, platform, product_name, \
                                self.tile )
        print out_dir
        pdb.set_trace()
        if not os.path.exists ( out_dir ):
            os.makedirs ( out_dir )
        output_files = []
        for fecha in get_dates:
            self.ftp.cwd ( "%s"%fecha )
            fichs = []
            self.ftp.dir ( fichs.append )
            grab = [ f for f in fichs if f.find( self.tile ) >= 0 ]
            for grab_file in grab:
                fname = grab_file.split()[7]
                f_out = open( os.path.join ( out_dir, fname), 'w')
                output_files.append ( os.path.join ( out_dir, fname) )
                print os.path.join ( out_dir, fname)
                pdb.set_trace()
                # Download the file a chunk at a time
                # Each chunk is sent to handleDownload
                # RETR is an FTP command
                print 'Getting ' + fname
                #
                def handle_download(block):
                    f_out.write(block)
                    f_out.flush()
                    print ".",
                    sys.stdout.flush()
                self.ftp.retrbinary('RETR ' + fname, handle_download )
                print 
                f_out.close()

        return output_files