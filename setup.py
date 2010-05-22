from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='modisficator',
      version=version,
      description="A package to work and download MODIS files.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='modis remotesensing geospatial',
      author='Jose Gomez-Dans',
      author_email='j.gomez-dans@geog.ucl.ac.uk',
      url='http://www2.geog.ucl.ac.uk/~ucfajlg/',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
