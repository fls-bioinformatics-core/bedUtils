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

# Set default logging level and output
logging.basicConfig(format='%(levelname)s: %(message)s')

#######################################################################
# Classes
#######################################################################

class TabFile:
    """Class to get data from a tab-delimited file

    Loads data from the specified file into a data structure than can
    then be queried on a per line and per item basis.

    Data lines are represented by TabDataLine objects.

    Example usage:

        data = TabFile(myfile)     # load initial data

        print '%s' % len(data)     # report number of lines of data

        print '%s' % data.header() # report header (i.e. column names)

        for line in data:
            ...                    # loop over lines of data

        myline = data[0]           # fetch first line of data
    """
    def __init__(self,filen,column_names=None,skip_first_line=False,
                 first_line_is_header=False):
        """Create a new TabFile object

        Arguments:
          filen: name of tab-delimited file to load
          column_names: (optional) list of column names to assign to
              columns in the file
          skip_first_line: (optional) if True then ignore the first
              line of the input file
          first_line_is_header: (optional) if True then takes column
              names from the first line of the file (over-riding
              'column_names' argument if specified.
        """
        # Initialise
        self.__filen = filen
        self.__ncols = 0
        # Set up column names
        self.__header = []
        if column_names is not None:
            self.setHeader(column_names)
        # Read in data
        self.__data = []
        self.load(skip_first_line=skip_first_line,
                  first_line_is_header=first_line_is_header)

    def load(self,skip_first_line=False,first_line_is_header=False):
        """Load data into the object from file

        *** Should not be called externally ***

        Lines starting with '#' are ignored (unless the first_line_is_header
        is set and the first line starts with '#').

        If a header is set then lines with fewer data items than header
        items raise an IndexError exception.

        Arguments:
          skip_first_line: (optional) if True then ignore the first
              line of the input file
          first_line_is_header: (optional) if True then take column
              names from the first line of the file
        """
        line_no = 0
        fp = open(self.__filen,'rU')
        for line in fp:
            line_no += 1
            if skip_first_line:
                # Skip first line
                skip_first_line = False
                continue
            elif first_line_is_header:
                # Set up header from first line
                self.setHeader(line.strip().strip('#').split('\t'))
                first_line_is_header = False
                continue
            if line.lstrip().startswith('#'):
                # Skip commented line
                continue
            # Store data
            data_line = TabDataLine(line,column_names=self.header())
            if self.__ncols > 0 and len(data_line) < self.__ncols:
                # Inconsistent lines are an error
                logging.error("L%d: fewer data items in line than expected" % line_no)
                raise IndexError, "Not enough data items in line"
            self.__data.append(data_line)
        fp.close()

    def setHeader(self,column_names):
        """Set the names for columns of data

        *** Should not be called externally ***

        Arguments:
          column_names: a tuple or list with names for each column in order.
        """
        if len(self.__header) > 0:
            logging.warning("Overriding existing headers")
            self.__header = []
        for name in column_names:
            self.__header.append(name)
        self.__ncols = len(self.__header)

    def header(self):
        """Return list of column names

        If no column names were set then this will be an empty list.
        """
        return self.__header

    def __getitem__(self,key):
        return self.__data[key]

    def __len__(self):
        return len(self.__data)

class TabDataLine:
    """Class to store a line of data from a tab-delimited file

    Values can be accessed by integer index or by column names (if
    set), e.g.

        line = TabDataLine("1\t2\t3",('first','second','third'))

    allows the 2nd column of data to accessed either via line[1] or
    line['second'].

    Values can also be changed, e.g.

        line['second'] = new_value

    Subsets of data can be created using the 'subset' method.
    """
    def __init__(self,line=None,column_names=None):
        """Create a new TabFileLine object

        Arguments:
          line: (optional) Tab-delimited line with data values
          column_names: (optional) tuple or list of column names
            to assign to each value.
        """
        self.names = []
        if column_names:
            for name in column_names:
                self.names.append(name)
        self.data = []
        if line is not None:
            self.data = line.strip().split('\t')

    def __getitem__(self,key):
        try:
            return self.data[int(key)]
        except ValueError:
            # See if key is a column name
            try:
                i = self.names.index(key)
            except ValueError:
                # Not a column name
                raise KeyError, "column '%s' not found" % key
            # Return the data
            return self.data[i]

    def __setitem__(self,key,value):
        self.data[int(key)] = value

    def __len__(self):
        return len(self.data)

    def append(self,*values):
        """Append values to the data line

        Should only be used when creating new data lines.
        """
        for value in values:
            self.data.append(value)

    def subset(self,*keys):
        """Return a subset of data items

        This method creates a new TabFileLine instance with a
        subset of data specified by the 'keys' argument, e.g.

            new_line = line.subset(2,1)

        returns an instance with only the 2nd and 3rd data values
        in reverse order.
        
        Arguments:
          keys: one or more keys specifying columns to include in
            the subset. Keys can be column indices, column names,
            or a mixture, and the same column can be referenced
            multiple times.
        """
        subset = TabFileLine(column_names=self.names)
        for key in keys:
            subset.append(self[key])
        return subset

    def __repr__(self):
        return '\t'.join(self.data)

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

