#!/bin/bash

# downloads NCI file from Google Drive using rclone: https://rclone.org/
# the NCI does not require filtering so it is better to keep this file separate.
# also, make sure to put a 0 in front of this filename in gdrive_filelist.csv so that it is not downloaded twice.

# use double-quotes if the path contains spaces
echo "Downloading data from Google Drive ..."

OUTDIR=data/ga/NCI/raw
mkdir -p $OUTDIR

rclone copy "gdrive:Theme A DCU/Irish_Data/ForasNaGaeilge/new-extraction/NCI_extracted_v2.txt" $OUTDIR --bwlimit 1000M --transfers 1

echo "Done"