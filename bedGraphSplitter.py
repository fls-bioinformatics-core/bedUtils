#!/bin/env python
#
#     microarraytowig.py: convert microarray data to wiggle format
#     Copyright (C) University of Manchester 2011 Peter Briggs
#
########################################################################
#
# bedGraphSplitter.py
#
#########################################################################

"""bedGraphSplitter.py

Create bedGraph format files from one or more columns in an input
tab-delimited file.

The UCSC bedGraph format is described here:
http://genome.ucsc.edu/goldenPath/help/bedgraph.html

The input file must have the first three columns as 'chromosome', 'start'
and 'end', followed by an arbitrary number of data columns.

There will be one output file for each selected column, each will contain
columns 'chromosome', 'start', 'end' and the data value from the selected
column.
"""

#######################################################################
# Import modules
#######################################################################

import os
import sys
import logging
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
    if len(sys.argv) < 2:
        print "Usage: %s [OPTIONS] <file>" % os.path.basename(sys.argv[0])
        print
        print "Generate bedGraph custom track files for display in UCSC browser from"
        print "genomic data taken from tab-delimited file."
        print
        print "<file> must have chromosome, start and end as the first three columns of"
        print "data. Use the --select option to pick one or more columns of data, each of"
        print "which will be output to a bedGraph format file, e.g."
        print
        print "\t%s --select=4,6,7 input.txt" % os.path.basename(sys.argv[0])
        print
        print "will create 3 bedGraph files with data from columns 4, 6 and 7 of the"
        print "input file."
        print 
        print "If the input file has column names in the first line then use the"
        print "--first-line-is-header option and use the column names in the --select"
        print "option, e.g."
        print
        print "\t%s --first-line-is-header --select='data 1','data 2' input.txt" \
            % os.path.basename(sys.argv[0])
        print
        print "Options"
        print
        print "  --select=<i>,[<j>,...]: write new file for each column <i>, <j>"
        print "    etc. Can either specifiy column numbers (starting from zero),"
        print "    or column names (if --first-line-is-header option is used)"
        print
        print "  --skip-first-line: ignore first line of input file"
        print
        print "  --first-line-is-header: take column names from first line of"
        print "    input file."
        print
        print "  --fix-chromosome: check and fix chromosome names in output file"
        print "    file (i.e. prepend 'chr' if missing)"
        sys.exit(1)

    # Initialise
    skip_first_line = False
    first_line_is_header = True
    fix_chromosome = False
    selected = []

    # Arguments
    filen = sys.argv[-1]
    for arg in sys.argv[1:-1]:
        if arg.startswith('--select='):
            selected = arg.split('=')[1].split(',')
            print "Selected columns = %s" % ' '.join(selected)
        elif arg == '--skip-first-line':
            skip_first_line = True
        elif arg == '--first-line-is-header':
            first_line_is_header = True
        elif arg == '--fix-chromosome':
            fix_chromosome = True
        else:
            print "Unrecognised argument: %s" % arg
            sys.exit(1)

    # Selected columns
    if len(selected) == 0:
        print "No columns selected for output."
        sys.exit()

    # Get the input data
    data = TabFile(filen,
                   skip_first_line=skip_first_line,
                   first_line_is_header=first_line_is_header)
    print "Got %d lines" % len(data)
    print "%s" % data.header()
    
    # Output files
    output_root = os.path.splitext(os.path.basename(filen))[0]
    output_ext = os.path.splitext(os.path.basename(filen))[1]
    out_file = {}
    for col in selected:
        filen_out = str(output_root+"_"+str(col)+".bedGraph").replace(' ','_')
        print "%s" % filen_out
        out_file[col] = open(filen_out,'w')
        # Write initial bedGraph track line
        out_file[col].write('track type=bedGraph name="%s" description="BedGraph format" ' % col)
        out_file[col].write('visibility=full color=2,100,0 altColor=0,100,200 priority=20\n')

    # Fix chromosome?
    if fix_chromosome:
        for line in data:
            if not line[0].startswith('chr'):
                line[0] = 'chr'+line[0]

    # Write to each file
    for line in data:
        for col in selected:
            out_file[col].write("%s\n" % line.subset(0,1,2,col))

    # Close output files
    for col in selected:
        out_file[col].close()

    print "Finished"
    sys.exit()

