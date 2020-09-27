#!/bin/bash

# downloads filelist from Google Drive using rclone: https://rclone.org/

# use double-quotes if the path contains spaces
echo "Downloading filelist from Google Drive ..."

OUTDIR=data/ga/gdrive

rclone copy "gdrive:Theme A DCU/Irish_Data/gdrive_filelist.csv" $OUTDIR

echo "Done"