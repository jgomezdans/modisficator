====================
MODISficator
====================

Introduction
------------

The MODIS data pool is an FTP server that contains all of the MODIS data archive (as well as ASTER, but that's for another day). The purpose of the current module is to make accessing the data in this archive as easy and painless as possible. Historically, acquiring MODIS data products required the user placing an order through the WIST system. After a while, an email was sent with a set of links to the different data granules. The current module improves on this state of affairs by providing an easy interface to the data, so that data that are not currently in the system can be directly downloaded (and tracked). It also has a database of available local holdings, that gets updated with new data downloads. Additionally, there is a facility to connect to the MODIS XML webservice to request individual pixels or groups of pixels.

Usage
------

The main function is an iterator, and as such, it can be used within a ``for`` loop in python:
::

    >>> from modisficator import get_modis_data
    >>> for retval in get_modis_data( "h17v04", "MOD14A1", \
                "2006-07-25", "2006-08-25" ):
    ...     print retval
    (datetime.datetime(2006, 7, 28, 0, 0), \
    '/data/geospatial_12/users/ucfajlg/MODIS/TERRA/MOD14A1/h17v04/\
              MOD14A1.A2006201.h17v04.005.2008141041008.hdf', \
    '/data/geospatial_12/users/ucfajlg/MODIS/TERRA/MOD14A1/h17v04/\
              BROWSE.MOD14A1.A2006201.h17v04.005.2008141041030.8.jpg', \
    '/data/geospatial_12/users/ucfajlg/MODIS/TERRA/MOD14A1/h17v04/\
              MOD14A1.A2006201.h17v04.005.2008141041008.hdf.xml')

    
In this case, the code requests the product ``MOD14A1`` (MODIS gridded daily active fires) for tile ``h17v04`` between the two specified dates (25/07/2006 and 25/08/2006). ``retval`` is a dictionary that contains the following elements:
    
    1. The date (a datetime object, use ``strftime`` or something like that to modify it).
    2. The (complete, UCL-system) path to the HDF file.
    3. The (complete, UCL-system) path to a quicklook file (if it's available).
    4. The (complete, UCL-system) path to an XML metadata file.

If the data are present in the system, the iterator proceeds very quickly. However, if the data are not present, it will proceed to download the data from the FTP site, and will only go through a loop iteration when the data have finisehd downloading and have been added to the database.


Architecture
------------

The system's architecture is quite simple. It is based on a database backend (either SQLite for single user systems, or Postgresql for multiuser systems, as is the case in UCL). There are a number of default settings to where things are downloaded to, and extensive loggig of the software is stored. In general, one can hope to find his/her downloads in ``/data/geospatial_12/$USERNAME/MODIS``, in a tree structure. The ``log`` directory contains log files of previous runs, which may be useful for debugging. There are other default actions taken in the code, which are hardwired, such as the choice of collection 5 data.

Things still to do
------------------

Perhaps the most important thing is a graceful way to add to the database data people have already downloaded. This raises a few questions:

    1. Data can be duplicated between different users.
    2. MODIS data are reprocessed constantly, we usually only want the latest version of each granule.

In practice, this data discovery effort could be implemented by a script that traverses the user's storage, locates MODIS files, and checks that they are not in the database. If they are, it checks that those in the database have a more recent reprocessing data, and then (i) removes the file, and (ii) replaces it with a symbolic link to the file already in the database. Else, the database entry is removed, replaced by the new file, and the original older data granule is removed and replaced by a symbolic link to the newer data granule. In theory this would allow users to still keep using their data (unless they hardwired the complete filenames in their codes, but nobody does *that*!), but it would likely lead to all sorts of permission problems. A first effort to insert data into the database is given in the ``dump_to_db.py`` script.

A practical problem is that the MODIS server goes down on Wednesdays, so processes should sleep if they cannot connect to the server at the maintenance downtime period.

