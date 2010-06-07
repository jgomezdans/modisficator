An example of usage
===================

Introduction
------------

Consider the following user case: A user wants to check pre- and post-fire nadir normalised reflectance from active fire detections. This suggests that the user wants to use the MOD14A1 product, locate the active fires, and then use data from the MCD43A4 product, maybe with a time window to account for missing observations or filtering of low quality MCD43 granules.

Take as a given that the user knows the tile and temporal range that s/he wants to consider. The task can then be effectively completed by

    1. Downloading the MOD14A1 product.
    2. Locating the active fires (raster values 8 or 9), and reporting its location (longitude, latitude, for example).
    3. Locating the pre- and post-fire NBAR reflectance data.
    4. Filtering the reflectance using QA flags
    5. Doing some sort of analysis.

The first two steps can be accomplished with the following script (the data have already been processed, but a function is given that deals with the MOD14A1 data):

.. plot:: ./plot_af.py
   :include-source: