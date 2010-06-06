# -*- coding: utf-8 -*-

"""
A script to traverse NASA's MODIS data site, and to extract product names
and dates.
"""
import ftplib
import time

ftp_host = "e4ftl01u.ecs.nasa.gov"
ftp = ftplib.FTP ( ftp_host, user="anonymouse", \
            password="j.gomez-dans@geog.ucl.ac.uk" )

platform_dir = {"TERRA":"/MOLT/", "AQUA":"/MOLA/", \
                        "COMBINED":"/MOTA/"}
for directory, platform in platform_dir.iteritems():
    ftp.cwd ("%s" % directory )
    products = []

    def parse(line):
        if line[0] == 'd':
            products.append(line.rpartition(' ')[2])

    ftp.dir( parse )

    for product in products:
        print platform, product