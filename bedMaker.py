#!/bin/env python
#
#     bedMaker.py: create BED file from tab-delimited data file
#     Copyright (C) University of Manchester 2011 Peter Briggs
#
########################################################################
#
# bedMaker.py
#
#########################################################################

"""bedMaker.py

Create BED format file from tab-delimited input file.

The UCSC bedGraph format is described here:
http://genome.ucsc.edu/FAQ/FAQformat.html#format1

The input file must have the following columns:

'chromosome'
'start'
'stop'
'strand'
'transcript'
'fold change'
'P value'

Additional columns can be present but will be ignored.

The output BED file will have columns:

'chromosome'
'start'
'stop'
'name'
'P value'
'strand'
'start'
'stop'
'RGB'

'stop' is the 'stop' position in the input minus one base.

'name' is constructed as '<transcript>_fc<fold_change>'

RGB values are set based on the P value of the line:

  p < 0.001 => 255,0,0
  p < 0.05  => 205,0,0
  p >= 0.05 => 139,0,0

"""

#######################################################################
# Import modules
#######################################################################

import os
import sys
import logging
from bedMakerUtils import BedMaker,prependChromosomeName,adjustStopPosition
import version
__version__ = version.__version__

# Set default logging level and output
logging.basicConfig(format='%(levelname)s: %(message)s')

#######################################################################
# Classes
#######################################################################

# No classes defined

#######################################################################
# Functions
#######################################################################

def computeRGB(p_value):
    """Set the RGB value based on the P value
    """
    if p_value < 0.001:
        RGB = '255,0,0'
    elif p_value < 0.05:
        RGB = '205,0,0'
    else:
        RGB = '139,0,0'
    return RGB
    
#######################################################################
# Main program
#######################################################################

if __name__ == "__main__":

    print "Version: %s" % __version__

    # Command line
    if len(sys.argv) != 2:
        print "Usage: %s <input_file>" % os.path.basename(sys.argv[0])
        sys.exit()

    print "Version: %s" % __version__

    # Internal flags
    fix_chromosome_name = True
    correct_stop_position = True

    # Input file
    infile = sys.argv[1]

    # Track name, description and output file name
    track_name = os.path.splitext(os.path.basename(infile))[0]
    track_description = track_name
    outfile = os.path.splitext(os.path.basename(infile))[0] + ".bed"
    print "Output file: %s" % outfile

    # Read in data
    data = BedMaker(infile,column_names=('chr','start','stop','strand','transcript',
                                         'fold_change','p_value'))
    
    # Fix chromosome name
    if fix_chromosome_name:
        print "Prepending 'chr' to chromosome names"
        prependChromosomeName(data,'chr')

    # Subtract one from end position
    if correct_stop_position:
        print "Correcting 'stop' position by subtracting one base"
        adjustStopPosition(data)

    # Set name and RBG values
    data.computeColumn('name',lambda line: "%s_fc%s" % (line['transcript'],line['fold_change']))
    data.computeColumn('RGB',lambda line: computeRGB(line['p_value']))

    # Write out lines to BED
    print "Writing data to BED file"
    data.makeBedFile(outfile,track_name,track_description,column_names=('chr','start','stop',
                                                                        'name','p_value',
                                                                        'strand','start','stop',
                                                                        'RGB'))
    print "Finished"
