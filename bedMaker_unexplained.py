#!/bin/env python
#
#     bedMaker_unexplained.py: create BED file from tab-delimited data file
#     Copyright (C) University of Manchester 2011 Peter Briggs
#
########################################################################
#
# bedMaker_unexplained.py
#
#########################################################################

"""bedMaker_unexplained.py

Create BED format file from tab-delimited input file.

The UCSC bedGraph format is described here:
http://genome.ucsc.edu/FAQ/FAQformat.html#format1

The input file must have the following columns:

'Chromosome'
'Start'
'Stop'
'Sample ID'
'Length'
'Average Coverage'

Additional columns can be present but will be ignored.

The output BED file will have columns:

'chromosome'
'start'
'stop'
'name'
'score'
'strand'
'start'
'stop'
'RGB'

'stop' is the 'stop' position in the input minus one base.

'name' is constructed as '<sample_id>_<length>bp'

'score' is the integer value of 'average coverage', with values over
1000 set to 1000.

RGB values are set based on the average coverage and length:

  average_coverage and length > 300 => -0,0,255
  else => 139,0,0

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

def computeRGBUnexplained(length,average_coverage):
    """Set the RGB value for the 'unexplained' output

    The RGB colour value is based on the length and average coverage
    values.
    """
    if length > 300 and average_coverage > 300:
        RGB = '0,0,255'
    else:
        RGB = '139,0,0'
    return RGB

#######################################################################
# Main program
#######################################################################

if __name__ == "__main__":
    
    # Command line
    if len(sys.argv) != 2:
        print "Usage: %s <input_file>" % os.path.basename(sys.argv[0])
        sys.exit()

    # Internal flags
    fix_chromosome_name = False
    correct_stop_position = True

    # Input file
    infile = sys.argv[1]

    # Track name, description and output file name
    track_name = os.path.splitext(os.path.basename(infile))[0]
    track_description = track_name
    outfile = os.path.splitext(os.path.basename(infile))[0] + ".bed"
    print "Output file: %s" % outfile

    # Read in data
    data = BedMaker(infile,column_names=('chr','start','stop','sample_id','length',
                                         'average_coverage'))
    
    # Fix chromosome name
    if fix_chromosome_name:
        print "Prepending 'chr' to chromosome names"
        prependChromosomeName(data,'chr')

    # Subtract one from end position
    if correct_stop_position:
        print "Correcting 'stop' position by subtracting one base"
        adjustStopPosition(data)

    # Set name, strand, score and RBG values
    data.computeColumn('name',lambda line: "%s_%sbp" % (line['sample_id'],line['length']))
    data.computeColumn('strand',lambda line: "+")
    data.computeColumn('score',lambda line: min(int(line['average_coverage']),1000))
    data.computeColumn('RGB',lambda line: computeRGBUnexplained(line['length'],
                                                                line['average_coverage']))

    # Write out lines to BED
    print "Writing data to BED file"
    data.makeBedFile(outfile,track_name,track_description,column_names=('chr','start','stop',
                                                                        'name','score',
                                                                        'strand','start','stop',
                                                                        'RGB'))
    print "Finished"
