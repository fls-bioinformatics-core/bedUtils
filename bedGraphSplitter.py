#!/bin/env python
#
#     bedGraphSplitter.py: split data file into multiple files by column
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
import optparse

# Set up for local modules in "share"
SHARE_DIR = os.path.abspath(
    os.path.normpath(
        os.path.join(os.path.dirname(sys.argv[0]),'..','share')))
sys.path.append(SHARE_DIR)
from TabFile import TabFile
import version
__version__ = version.__version__

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

    p = optparse.OptionParser(usage="%prog [options] <file>",
                              version="%prog "+__version__,
                              description=
                              "Generate bedGraph custom track files for display in UCSC "
                              "browser from genomic data taken from tab-delimited file"
                              "containing chromosome, start and end as the first three "
                              "columns of data. Use the --select option to pick one or more "
                              "columns, each of which will be output to a bedGraph format "
                              "file.")

    p.add_option('--select',action='store',dest='selection',default=None,
                 help="specify columns from input file as one or more column indices "
                 "(i.e. where 1 is the first column) or column names (if "
                 "--first-line-is-header is used). If multiple columns are selected "
                 "then separate them by commas, e.g. '4,6,7'. A bedGraph file will "
                 "be output for each of the selected columns specified.")
    p.add_option('--skip-first-line',action="store_true",dest="skip_first_line",
                 help="skip first line of input file")
    p.add_option('--first-line-is-header',action="store_true",dest="first_line_is_header",
                 help="take column names from first line of input file")
    p.add_option('--fix-chromosome',action="store_true",dest="fix_chromosome",
                 help="fix chromosome names in output file file, by prepending 'chr' "
                 "if missing in the input")
    p.add_option('--bedGraph-header',action="store",dest="header",default=None,
                 help="specify text to use as the header for each output bedGraph "
                 "(default is not to write a header)")

    # Process the command line
    options,arguments = p.parse_args()

    # Input file
    if len(arguments) != 1:
        p.error("No input file supplied")
    filen = arguments[0]
    if not os.path.exists(filen):
        logging.error("Input file '%s' not found" % filen)
        sys.exit(1)

    # Report version
    p.print_version()

    # Initialise
    skip_first_line = options.skip_first_line
    first_line_is_header = options.first_line_is_header
    fix_chromosome = options.fix_chromosome
    bedgraph_header = options.header
    user_selected = str(options.selection).split(',')

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
            if col0 >= data.nColumns():
                logging.error("Unable to find column %s, not enough columns in input file" % col)
                sys.exit(1)
        except ValueError:
            # Not an integer
            if col not in data.header():
                logging.error("Unable to find column '%s' in input file" % col)
                sys.exit(1)
            col0 = data.header().index(col)
        # Column lookup
        col_lookup[col0] = col
        # Adjusted column names
        selected.append(col0)
        # File names
        if first_line_is_header:
            file_names[col0] = str(str(data.header()[col0])+".bedGraph").replace(' ','_')
        else:
            file_names[col0] = str(output_root+"_"+str(col)+".bedGraph").replace(' ','_')
    
    # Open output files
    out_file = {}
    print "Opening output files:"
    for col in selected:
        print "\t%s" % file_names[col]
        out_file[col] = open(file_names[col],'w')
        if bedgraph_header is not None:
            # Write bedGraph header
            out_file[col].write("%s\n" % bedgraph_header)

    # Fix chromosome?
    if fix_chromosome:
        print "Fixing chromosome names..."
        for line in data:
            if not str(line[0]).startswith('chr'):
                line[0] = 'chr'+str(line[0])

    # Fix end positions (subtract 1 base)
    fix_end_position = True
    if fix_end_position:
        print "Fixing end positions..."
        for line in data:
            try:
                line[2] = str(int(line[2])-1)
            except TypeError:
                logging.warning("Unable to fix end position for L%d" % line.lineno())

    # Write to each file
    print "Writing data..."
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

