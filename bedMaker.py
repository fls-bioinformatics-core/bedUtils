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

# No classes defined

#######################################################################
# Main program
#######################################################################

if __name__ == "__main__":

    # Command line
    if len(sys.argv) != 2:
        print "Usage: %s <input_file>" % os.path.basename(sys.argv[0])
        sys.exit()

    # Input file
    infile = sys.argv[1]

    # Track name, description and output file name
    track_name = os.path.splitext(os.path.basename(infile))[0]
    track_description = track_name
    outfile = os.path.splitext(os.path.basename(infile))[0] + ".bed"
    print "Output file: %s" % outfile

    # Read in data
    data = TabFile(infile,
                   column_names=('chr','start','stop','strand','transcript',
                                 'fold_change','p_value'))

    # Check if first line is real data
    if len(data) > 0:
        if not data[0]['start'].isdigit() or \
                not data[0]['stop'].isdigit():
            print "First line doesn't look like data, removing"
            del(data[0])

    # Create new (empty) tabfile for output
    fo = open(outfile,'w')

    # Write BED file header
    fo.write('track name="%s" description="%s" visibility=pack itemRgb="On"\n' %
             (track_name,track_description))

    # Write out lines to BED
    for line in data:
        # Check there's data
        if str(line).strip() == '':
            print "No data items on line %d, ignoring" % line.lineno()
            continue
        # Fix chromosome
        line['chr'] = 'chr' + line['chr']
        # Construct computed values
        name = "%s_fc%s" % (line['transcript'],line['fold_change'])
        try:
            p_value = float(line['p_value'])
        except ValueError:
            print "Error: couldn't convert p-value to float (line %d): '%s'" % \
                (line.lineno(),line['p_value'])
            sys.exit(1)
        if p_value < 0.001:
            RGB = '255,0,0'
        elif p_value < 0.05:
            RGB = '205,0,0'
        else:
            RGB = '139,0,0'
        # Write out the line
        fo.write("%s\n" % '\t'.join((line['chr'],
                                     line['start'],
                                     line['stop'],
                                     name,
                                     line['p_value'],
                                     line['strand'],
                                     line['start'],
                                     line['stop'],
                                     RGB)))
    # Finished, close file
    fo.close()
