# -*- coding: utf-8 -*-

"""
A script to traverse NASA's MODIS data site, and to extract product names
and dates.
"""
import ftplib
import time
import pdb

ftp_host = "e4ftl01u.ecs.nasa.gov"
ftp = ftplib.FTP ( ftp_host, user="anonymous", \
            passwd="j.gomez-dans@geog.ucl.ac.uk" )

platform_dir = {"TERRA":"/MOLT/", "AQUA":"/MOLA/", \
                        "COMBINED":"/MOTA/"}
products = {}
for platform, directory in platform_dir.iteritems():
    ftp.cwd ("%s" % directory )
    products[platform] = []

    def parse(line):
        if line[0] == 'd' or line[0] == "l":
            products[platform].append(line.rpartition(' ')[0].split()[-2])

    ftp.dir( parse )
fp = open ("modis_ftp_vault.txt", 'w' )
for platform in products.iterkeys():
    for product in products[platform]:
        print platform, product
        try:
            ftp.cwd ( "%s%s"% ( platform_dir[platform], product ) )
        except ftplib.error_perm:
            print 'Skipping %s%s!!' % ( platform_dir[platform], product )
            continue
        dates = []
        def parse(line):
            if line[0] == 'd' or line[0] == "l":
                dates.append( line.rpartition(' ')[-1] )
        ftp.dir ( parse )
        try:
            dates = [ time.strptime(d, "%Y.%m.%d") for d in dates ]
            start_date = time.strftime("%Y-%m-%d", dates[0] )
            end_date = time.strftime("%Y-%m-%d", dates[-1] )
            periodicity = dates[1].tm_yday- dates[0].tm_yday
            print "%s,%s,%s,%s,%s,%d\n" % ( platform, product, "%s%s" %\
                ( platform_dir[platform], product ), \
                start_date, end_date, periodicity )
            fp.write("%s,%s,%s,%s,%s,%d\n" % ( platform, product, "%s%s" %\
                    ( platform_dir[platform], product ), \
                    start_date, end_date, periodicity ))
        except:
            print 'Skipping %s%s!!' % ( platform_dir[platform], product )
            continue
ftp.close()
fp.close()
    
