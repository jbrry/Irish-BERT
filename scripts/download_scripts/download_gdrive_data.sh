#!/bin/bash

# downloads files from Google Drive using rclone: https://rclone.org/

# use double-quotes if the path contains spaces
echo "Downloading data from Google Drive ..."

OUTDIR=data/ga/gdrive

rclone copy "gdrive:Theme A DCU/Irish_Data/" $OUTDIR --bwlimit 10M --transfers 1 --progress

echo "Done"

