#!/bin/env python
#
#     bedMakerUtils.py: utilities for creating BED files from tabbed data
#     Copyright (C) University of Manchester 2011 Peter Briggs
#
########################################################################
#
# bedMakerUtils.py
#
#########################################################################

"""bedMakerUtils.py

Utility classes and functions for creating BED format files from tab-delimited
input files.

The UCSC bedGraph format is described here:
http://genome.ucsc.edu/FAQ/FAQformat.html#format1

The core class is the 'BedMaker' class, which reads in initial data from a
tab-delimited file and then allows the data to be manipulated, extra columns
to be added etc, before being output as a BED format file.

Basic usage is:

>>> from bedMakerUtils import BedMaker
>>> bed = BedMaker('myfile',column_name=('chr','start','stop',...))
>>> ... add additional columns ...
>>> bed.writeBedFile('myfile.bed','custom track','custom track',column_names=(...))

There are also two convenience functions:

* prependChromosomeName: adds a prefix to the chromosome names in a TabFile
* adjustStopPosition: removes one base from the stop position values
"""

#######################################################################
# Import modules
#######################################################################

import os
import sys
import logging
import version
__version__ = version.__version__

# Set up for local modules in "share"
SHARE_DIR = os.path.abspath(
    os.path.normpath(
        os.path.join(os.path.dirname(sys.argv[0]),'..','share')))
sys.path.append(SHARE_DIR)
from TabFile import TabFile

# Set default logging level and output
logging.basicConfig(format='%(levelname)s: %(message)s')

#######################################################################
# Classes
#######################################################################

class BedMaker(TabFile):
    """BedMaker

    Class for creating BED format files from arbitrary tab-delimited
    data files.

    Basic usage:
    
    1. Read in data from the source file, e.g.:

    >>> bed = BedMaker(infile,column_names=('chr','start','stop'...)

    2. Add or transform columns as required, e.g.:

    >>> bed.computeColumn('RGB',RGBfunc)

    3. Write out the data to a BED file, e.g.:

    >>> bed.writeBedFile(outfile,name,description,column_names=('chr','start','stop'...)
    """

    def __init__(self,infile,column_names):
        """Create a new BedMaker instance

        Arguments:
          infile: tab-delimited data file to read initial data from
          column_names: names to assign to data columns read in from the file
        """
        # Initialise base class
        TabFile.__init__(self,infile,column_names=column_names)
        # Check if first line is real data
        if len(self) > 0:
            if not self[0]['start'].isdigit() or \
                    not self[0]['stop'].isdigit():
                print "First line of input file doesn't look like data, removing"
                del(self[0])
        # Remove blank lines
        i = 0
        while i < len(self):
            if not str(self[i]).strip():
                del(self[i])
            else:
                i += 1

    def makeBedFile(self,bedout,name,description,column_names):
        """Write the data as a BED format file

        Creates a BED file with columns populated with data from the named
        columns, which can either have been read in from the source file or
        created subsequently.

        Note that the same column name can appear more than once in the
        list of output column names.

        Arguments:
          bedout: name of the output file to write to
          name: text to put in the 'name' field of the 'track' header
          description: text to put in the 'description' field of the 'track'
            header
          column_names: list of the column names to write to the BED file
        """
        # Write the output BED file header
        fo = open(bedout,'w')
        fo.write('track name="%s" description="%s" visibility=pack itemRgb="On"\n' %
             (name,description))
        # Write data
        for line in self:
            # Check there's data
            if str(line).strip() == '':
                print "No data items on line %d, ignoring" % line.lineno()
                continue
            # Write out the line
            fo.write("%s\n" % str(line.subset(*column_names)))
        # Finished
        fo.close()

#######################################################################
# Functions
#######################################################################

def prependChromosomeName(tabfile,prefix):
    """Add a prefix to the chromosome names in a TabFile

    Prefix all values in the 'chr' column of a TabFile or TabFile-derived
    object with the supplied string.
    """
    prefix_str = str(prefix)
    for data in tabfile:
        if not str(data['chr']).startswith('chr'):
            data['chr'] = prefix_str + str(data['chr'])

def adjustStopPosition(tabfile):
    """Adjust the stop positions in a TabFile

    Subtract 1 base from all the values in the 'stop' column of a TabFile or
    TabFile-derived object.
    """
    tabfile.transformColumn('stop',lambda stop: stop - 1)
