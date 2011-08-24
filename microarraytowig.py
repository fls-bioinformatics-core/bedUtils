import os
import sys
if __name__ == "__main__":
    # Check command line
    if len(sys.argv) !=3:
        print "Usage: %s <probeset>.bed <microarray_data>.txt" % (sys.argv[0])
        sys.exit(1)
    # Open probeset file and get list of probeset id's
    probeset_ids = []
    fp = open(sys.argv[1],'r')
    for line in fp:
        probeset_ids.append(line.split('\t')[0])
    fp.close()
    # Get microarray file basename
    ma_basename = os.path.splitext(os.path.basename(sys.argv[2]))[0]
    print "Basename: %s" % ma_basename
    # Open microarray file
    fm = open(sys.argv[2],'r')
    # Read microarray header - first line of file
    # Make an output file for each column
    header = fm.readline()
    header = header.split()
    files = []
    print "Columns = %d" % len(header)
    print "%s" % header
    for name in header[1:]:
        print "Would open %s" % ma_basename+"_"+name+".wig"
        ##fp = open(name+".wig",'w')
        ##files.append(fp)
        files.append(ma_basename+"_"+name+".wig")
    # Convenience variable
    nfiles = len(files)
    # for each line in microarray file
    # check if the id (first value) is in the probeset list
    stop = 0
    skipped = 0
    read = 0
    for line in fm:
        items = line.strip().split()
        id = items[0]
        try:
            # Check if this id is in the list of probeset ids
            # If not then an IndexError is raised 
            i = probeset_ids.index(id)
            # Add values to appropriate file
            ##for j in range(nfiles):
                ##files[j].write(items[j+1])
                ##print "%s: %s" % (files[j],items[j+1])
            stop += 1
            read += 1
        except IndexError:
            # Not found
            ##print "Skipped"
            skipped += 1
            pass
        if stop == 100:
            break
    # Finished
    fm.close()
    ##for f in files:
    ##    f.close()
    print "Read %d Skipped %d" % (read,skipped)
    
