#!/bin/bash

# downloads the Oscar corpus from Google Drive using rclone: https://rclone.org/
# use double-quotes if the path contains spaces
OUTDIR=data/ga/oscar/raw

# Download Oscar corpus
if [ -s "$OUTDIR" ]; then
    echo "$OUTDIR exists, skipping download." >&2
else
    mkdir -p ${OUTDIR}
    echo $'\n'"Downloading Oscar data for ga..."$'\n'
    rclone copy "gdrive:Theme A DCU/ga_BERT/BERT_Preprocessing/raw-corpora/oscar-ga-unshuffled.tar.bz2" $OUTDIR --bwlimit 1000M --transfers 1
fi  

echo "Done"

