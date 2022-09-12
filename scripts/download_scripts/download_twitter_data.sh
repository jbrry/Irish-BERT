#!/bin/bash

# downloads collected twitter data from Google Drive using rclone: https://rclone.org/
# make sure to put a 0 in front of these files in gdrive_filelist.csv so that it is not downloaded twice.

# use double-quotes if the path contains spaces
echo "Downloading twitter data from Google Drive ..."

OUTDIR=data/ga/twitter/raw
mkdir -p $OUTDIR

if [[ -n $(rclone lsf --drive-shared-with-me "gdrive:Theme A DCU" 2> /dev/null) ]]; then
    THEME_A_DCU="gdrive:Theme A DCU"
else
    if [[ -n $(rclone lsf --drive-shared-with-me "gdrive:Theme A/Theme A DCU" 2> /dev/null) ]]; then
        THEME_A_DCU="gdrive:Theme A/Theme A DCU"
    else
        echo "Theme A DCU folder not found"
        exit 1
    fi
fi

rclone copy --drive-shared-with-me "gdrive:Theme A DCU/Irish_Data/Tweets/" $OUTDIR --bwlimit 1000M --transfers 1

cd $OUTDIR
rm README.md
bzip2 *.txt

echo "Done"
