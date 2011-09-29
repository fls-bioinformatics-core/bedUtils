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
        print "    etc. Can either specifiy column numbers (starting from one),"
        print "    or column names (if --first-line-is-header option is used)"
        print
        print "  --skip-first-line: ignore first line of input file"
        print
        print "  --first-line-is-header: take column names from first line of"
        print "    input file"
        print
        print "  --fix-chromosome: check and fix chromosome names in output file"
        print "    file (i.e. prepend 'chr' if missing)"
        print
        print "  --bedGraph-header=<header>: by default the output bedGraph files"
        print "    don't have header text; use this option to specify text to use"
        print "    as the header for each bedGraph"
        sys.exit(1)

    # Initialise
    skip_first_line = False
    first_line_is_header = False
    fix_chromosome = False
    bedgraph_header = None
    user_selected = []

    # Arguments
    filen = sys.argv[-1]
    for arg in sys.argv[1:-1]:
        if arg.startswith('--select='):
            user_selected = arg.split('=')[1].split(',')
        elif arg == '--skip-first-line':
            skip_first_line = True
        elif arg == '--first-line-is-header':
            first_line_is_header = True
        elif arg == '--fix-chromosome':
            fix_chromosome = True
        elif arg.startswith('--bedGraph-header='):
            bedgraph_header = arg.split('=')[1]
        else:
            print "Unrecognised argument: %s" % arg
            sys.exit(1)

    # Get the input data
    data = TabFile(filen,
                   skip_first_line=skip_first_line,
                   first_line_is_header=first_line_is_header)
    print "Read in %d lines" % len(data)
    if first_line_is_header:
        print "Header:"
        for col in data.header():
            print "\t%s" % col

    # Output file
    output_root = os.path.splitext(os.path.basename(filen))[0]

    # Selected columns
    if len(user_selected) == 0:
        print "No columns selected for output."
        sys.exit()
    print "Selected columns = %s" % ' '.join(user_selected)
    # Assume user counts columns starting from one and adjust to count from zero
    # Also check that the requested column exists and set up file names based on
    # user input
    selected = []
    col_lookup = {}
    file_names = {}
    for col in user_selected:
        try:
            col0 = int(col) - 1
            if col0 >= len(data.header()):
                logging.error("Unable to find column %s, not enough columns in input file" % col)
                sys.exit(1)
        except ValueError:
            # Not an integer
            if col not in data.header():
                logging.error("Unable to find column '%s' in input file" % col)
                sys.exit(1)
            col0 = col
        # Column lookup
        col_lookup[col0] = col
        # Adjusted column names
        selected.append(col0)
        # File names
        file_names[col0] = str(output_root+"_"+str(col)+".bedGraph").replace(' ','_')
    
    # Open output files
    out_file = {}
    for col in selected:
        print "%s" % file_names[col]
        out_file[col] = open(file_names[col],'w')
        if bedgraph_header is not None:
            # Write bedGraph header
            out_file[col].write("%s\n" % bedgraph_header)

    # Fix chromosome?
    if fix_chromosome:
        for line in data:
            if not line[0].startswith('chr'):
                line[0] = 'chr'+line[0]

    # Write to each file
    for line in data:
        for col in selected:
            try:
                out_file[col].write("%s\n" % line.subset(0,1,2,col))
            except IndexError:
                logging.warning("Error outputting data for column '%s'" % col_lookup[col])

    # Close output files
    for col in selected:
        out_file[col].close()

    print "Finished"
    sys.exit()

