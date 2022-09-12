#!/bin/bash

# downloads the Oscar corpus from Google Drive using rclone: https://rclone.org/
# use double-quotes if the path contains spaces
OUTDIR=data/ga/oscar/raw
FILENAME=oscar-ga-unshuffled.tar.bz2

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

# Download Oscar corpus
if [ -s "$OUTDIR" ]; then
    echo "$OUTDIR exists, skipping download." >&2
else
    mkdir -p ${OUTDIR}
    echo $'\n'"Downloading Oscar data for ga..."$'\n'
    rclone copy --drive-shared-with-me "${THEME_A_DCU}/ga_BERT/BERT_Preprocessing/raw-corpora/${FILENAME}" $OUTDIR --bwlimit 1000M --transfers 1
    if [ -f "${OUTDIR}/${FILENAME}" ]; then
        # unzip/untar download
        cd ${OUTDIR}
        bzip2 -d oscar-ga-unshuffled.tar.bz2
        tar -xf oscar-ga-unshuffled.tar
        mv oscar/unshuffled/ga/oscar-ga-unshuffled.txt .
        echo "Done"
    else
        echo "Download failed"
        rmdir "${OUTDIR}"
        exit 1
    fi
fi  

