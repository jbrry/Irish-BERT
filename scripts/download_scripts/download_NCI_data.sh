#!/bin/bash

# downloads NCI file from Google Drive using rclone: https://rclone.org/
# the NCI does not require filtering so it is better to keep this file separate.
# also, make sure to put a 0 in front of this filename in gdrive_filelist.csv so that it is not downloaded twice.

# use double-quotes if the path contains spaces
echo "Downloading data from Google Drive ..."

OUTDIR=data/ga/NCI/raw
OUTFILE=${OUTDIR}/NCI_v2.txt

mkdir -p $OUTDIR

if [[ -n $(rclone lsf "gdrive:Theme A DCU" 2> /dev/null) ]]; then
    THEME_A_DCU="gdrive:Theme A DCU"
else
    if [[ -n $(rclone lsf "gdrive:Theme A/Theme A DCU" 2> /dev/null) ]]; then
        THEME_A_DCU="gdrive:Theme A/Theme A DCU"
    else
        echo "Theme A DCU folder not found"
        exit 1
    fi
fi

rclone cat \
    "${THEME_A_DCU}/Irish_Data/ForasNaGaeilge/9MqDsdf834ms2NfS8L2joi7u_NCIv2.vert" \
    --bwlimit 1000M --transfers 1 | \
    scripts/extract_text_from_nci_vert.py --document-newline | \
    bzip2 > ${OUTFILE}.bz2

# do not leave behind uncompressed file from a run with
# an older version of this script
rm -f ${OUTFILE}

echo "Done"
