#!/bin/sh
#
# Script to do microarray mapping
#
# Usage: microarray_mapper.sh <probeset_file> <exon_file> [ <liftover_chain> ]
usage="microarray_mapper.sh <probeset_file> <exon_file> [ <liftover_chain> ]"
#
export PATH=.:${PATH}
#
# Inputs
probeset_file=$1
exon_data=$2
liftover_chain=$3
#
# Basenames for files
probeset_basename=${probeset_file%.*}
probeset_basename=`basename $probeset_basename`
exons_basename=`basename ${exon_data%.*}`
#
# Get BED file for probeset
if [ ! -z "$probeset_file" ] ; then
    bed_file=${probeset_basename}.bed
    ./probeset2bed.py $probeset_file
else
    echo Usage: $usage
    echo No probset...fa file supplied
    exit 1
fi
#
# Do liftOver
if [ ! -z "$liftover_chain" ] ; then
    liftover=`which liftover`
    new_bed=${probeset_basename}_liftOver.bed
    unmapped=${probeset_basename}_unmapped
    ${liftOver} $bed_file $liftover_chain $new_bed $unmapped
    bed_file=$new_bed
else
    echo No liftOver chain file supplied, liftOver skipped
fi
#
# Cross-reference with exon data
if [ ! -z "$exon_data" ] ; then
    ./microarraytowig.py $bed_file $exon_data
else
    echo Usage: $usage
    echo No exon data supplied
    exit 1
fi
#
# Collect output files
bedgraphs=`ls ${exons_basename}_*.bedGraph`
#
# Sort using bedSort
bedsort=`which bedSort`
for bedgraph in $bedgraphs ; do
    echo Sorting $bedgraph
    ${bedsort} $bedgraph $bedgraph
done
#./bedSort $bedgraph $bedgraph
#
# Convert to BigWig using wigToBigWig
echo BigWig conversion not implemented
#
exit
##
#