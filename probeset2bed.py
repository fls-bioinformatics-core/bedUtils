#!/bin/env python
#
#     probeset2bed.py: create BED file from microarray probeset data
#     Copyright (C) University of Manchester 2011 Peter Briggs
#
########################################################################
#
# probeset2bed.py
#
#########################################################################

"""probeset2bed.py

Create BED file from microarray probeset data.
"""

#######################################################################
# Import modules
#######################################################################

import os
import sys

#######################################################################
# Main program
#######################################################################

if __name__ == "__main__":

    # Command line arguments
    if len(sys.argv) != 2:
        print "Usage: %s <probeset_file>.fa" % \
            os.path.basename(sys.argv[0])
        sys.exit(1)
    probeset_file = sys.argv[1]
    ##print "Index: %s" % probeset_file

    # Process the probeset file
    fp = open(probeset_file,'r')
    for line in fp:
        if line.startswith(">probe_set:"):
            # Process probset line
            # e.g. >probe_set:HuEx-1_0-st-v2:2315101; Assembly=build-34/hg16; Seqname=chr1; Start=1788; Stop=2030; Strand=+; Length=243; category=main
            fields = line.split(';')
            # First field should be "probeset"
            # e.g. >probe_set:HuEx-1_0-st-v2:2315101
            # Get the name and id
            name = fields[0].split(':')[1]
            id = fields[0].split(':')[2]
            # Seqname
            seqname = fields[2].split('=')[1]
            # Start
            start = fields[3].split('=')[1]
            # Stop
            stop = fields[4].split('=')[1]
            #
            print "%s\t%s\t%s\t%s" % (id,start,stop,name)
    fp.close()

    # Finished
