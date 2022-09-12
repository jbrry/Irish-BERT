#!/bin/bash

# downloads filelist from Google Drive using rclone: https://rclone.org/

# use double-quotes if the path contains spaces
echo "Downloading filelist from Google Drive ..."

OUTDIR=data/ga/gdrive

# @JF you will need to removed the shared option and adjust the path to Theme A DCU

rclone copy --drive-shared-with-me "gdrive:Theme A DCU/Irish_Data/gdrive_filelist.csv" $OUTDIR

echo "Done"
