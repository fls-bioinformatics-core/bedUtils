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

    >>> data = BedMaker(infile,column_names=('chr','start','stop'...)

    2. Add or transform columns as required, e.g.:

    >>> data.computeColumn('RGB',RGBfunc)

    3. Write out the data to a BED file, e.g.:

    >>> data.writeBedFile(outfile,name,description,column_names=('chr','start','stop'...)
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

    def transformColumn(self,column_name,transform_func):
        """Apply arbitrary function to a column

        For each line of data the transformation function will be invoked
        with the line as the sole argument, and the result will be stored in
        the named column (overwriting any existing value).

        Arguments:
          column_name: name of column to write transformation result to
          transform_func: callable object that will be invoked to perform
            the transformation
        """
        for line in self:
            try:
                line[column_name] = transform_func(line)
            except Exception, ex:
                logging.error("transformColumn raised exception for line %d" % line.lineno)
                raise ex

    def computeColumn(self,column_name,compute_func):
        """Compute and store values in a new column
    
        For each line of data the computation function will be invoked
        with the line as the sole argument, and the result will be stored in
        a new column with the specified name.

        Arguments:
          column_name: name of column to write transformation result to
          compute_func: callable object that will be invoked to perform
            the computation
        """
        self.appendColumn(column_name)
        for line in self:
            line[column_name] = compute_func(line)

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

def prependChromosomeName(data,prefix):
    prefix_str = str(prefix)
    data.transformColumn('chr',lambda line: prefix_str + str(line['chr']))

def adjustStopPosition(data):
    data.transformColumn('stop',lambda line: line['stop'] - 1)

def computeRGB(p_value):
    if p_value < 0.001:
        RGB = '255,0,0'
    elif p_value < 0.05:
        RGB = '205,0,0'
    else:
        RGB = '139,0,0'
    return RGB

def computeRGBUnexplained(length,average_coverage):
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
    ##fix_chromosome_name = True
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
    ##data = BedMaker(infile,column_names=('chr','start','stop','strand','transcript',
    ##                                     'fold_change','p_value'))
    # Unexplained input
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

    # Set name and RBG values
    ##data.computeColumn('name',lambda line: "%s_fc%s" % (line['transcript'],line['fold_change']))
    ##data.computeColumn('RGB',lambda line: computeRGB(line['p_value']))

    # Set name, strand, score and RBG values
    data.computeColumn('name',lambda line: "%s_%sbp" % (line['sample_id'],line['length']))
    data.computeColumn('strand',lambda line: "+")
    data.computeColumn('score',lambda line: min(int(line['average_coverage']),1000))
    data.computeColumn('RGB',lambda line: computeRGBUnexplained(line['length'],
                                                                line['average_coverage']))

    # Write out lines to BED
    print "Writing data to BED file"
    ##data.makeBedFile(outfile,track_name,track_description,column_names=('chr','start','stop',
    ##                                                                    'name','p_value',
    ##                                                                    'strand','start','stop',
    ##                                                                    'RGB'))
    data.makeBedFile(outfile,track_name,track_description,column_names=('chr','start','stop',
                                                                        'name','score',
                                                                        'strand','start','stop',
                                                                        'RGB'))
    print "Finished"
