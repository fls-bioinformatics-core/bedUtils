#!/bin/env python
#
#     microarraytowig.py: convert microarray data to wiggle format
#     Copyright (C) University of Manchester 2011 Peter Briggs
#
########################################################################
#
# microarraytowig.py
#
#########################################################################

"""microarraytowig.py

Convert microarray data to wiggle format.
"""

#######################################################################
# Import modules
#######################################################################

import os
import sys
import logging

#######################################################################
# Classes
#######################################################################

# ProbesetData
class ProbesetData:
    """Convenience class for storing data from probeset bed file.

    Initialise a ProbesetData with the information to be stored, which
    can then be accessed via the object's properties.
    """
    def __init__(self,probe_id,chrom,start,end):
        """New ProbesetData object

        Arguments:
          probe_id: probeset id number
          chrom:    chromosome
          start:    start coordinate
          end:      end coordinate
        """
        self.chrom = chrom
        self.start = start
        self.end = end
        self.id = probe_id

#######################################################################
# Main program
#######################################################################

if __name__ == "__main__":
    # Check command line
    if len(sys.argv) !=3:
        print "Usage: %s <probeset>.bed <microarray_data>.txt" % \
            os.path.basename(sys.argv[0])
        sys.exit(1)
    # Logging format and level
    logging.basicConfig(format='%(levelname)s %(message)s')
    logging.getLogger().setLevel(logging.DEBUG)
    # Open probeset file and get list of probeset id's
    probeset_ids = []
    probeset_data = []
    fp = open(sys.argv[1],'r')
    for line in fp:
        items = line.strip().split('\t')
        data = ProbesetData(items[3],items[0],items[1],items[2])
        probeset_data.append(data)
        probeset_ids.append(data.id)
    fp.close()
    logging.debug("Read in %s probeset ids" % len(probeset_ids))
    logging.debug("Probeset ids (first 20): %s" % probeset_ids[:20])
    # Get microarray file basename
    ma_basename = os.path.splitext(os.path.basename(sys.argv[2]))[0]
    logging.debug("Basename for output files: %s" % ma_basename)
    # Open microarray file
    fm = open(sys.argv[2],'r')
    # Read microarray header - first line of file
    # Make an output file for each column
    header = fm.readline()
    header = header.split()
    files = []
    logging.debug("Found %d columns in exon data header" % len(header))
    logging.debug("Header from exon data file: %s" % header)
    print "Output files (one per column in exon data file):"
    for name in header[1:]:
        filen = ma_basename+"_"+name+".bedGraph"
        print "\t%s" % filen
        fp = open(filen,'w')
        fp.write('track type=bedGraph name="%s" description="BedGraph format"\n' % name)
        fp.write('visibility=full color=2,100,0 altColor=0,100,200 priority=20\n')
        files.append(fp)
    # Convenience variable
    nfiles = len(files)
    # for each line in microarray file
    # check if the id (first value) is in the probeset list
    skipped = 0
    read = 0
    for line in fm:
        items = line.strip().split()
        probeset_id = items[0]
        read += 1
        if (read % 10000) == 0:
            print "Read %d" % read
        try:
            # Check if this id is in the list of probeset ids
            # If not then a ValueError is raised 
            i = probeset_ids.index(probeset_id)
            # Add values to appropriate file
            for j in range(nfiles):
                files[j].write("%s\t%s\t%s\t%s\n" % (probeset_data[i].chrom,
                                                     probeset_data[i].start,
                                                     probeset_data[i].end,
                                                     items[j+1]))
        except ValueError:
            # Not found
            logging.warning("Exon data has id not found in probeset data: %s" % probeset_id)
            skipped += 1
            pass
    # Finished
    logging.debug("Closing files")
    fm.close()
    for f in files:
        f.close()
    print "Finished: Read %d, skipped %d" % (read,skipped)
    
