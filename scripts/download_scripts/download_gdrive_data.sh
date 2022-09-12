#!/bin/bash

# downloads files from Google Drive using rclone: https://rclone.org/

# use double-quotes if the path contains spaces
echo "Downloading data from Google Drive ..."

OUTDIR=data/ga/gdrive
mkdir -p $OUTDIR

# @JF you will need to removed the shared option and adjust the path to Theme A DCU

rclone copy --drive-shared-with-me "gdrive:Theme A DCU/Irish_Data/" $OUTDIR --bwlimit 1000M --transfers 1

echo "Done"

