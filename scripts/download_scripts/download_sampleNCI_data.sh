#!/bin/bash

# downloads NCI file from Google Drive using rclone: https://rclone.org/
# the NCI does not require filtering so it is better to keep this file separate.
# also, make sure to put a 0 in front of this filename in gdrive_filelist.csv so that it is not downloaded twice.

# use double-quotes if the path contains spaces

OUTDIR=data/ga/sampleNCI/raw
SHUF_RANDOM_SEED=101
SAMPLE_SIZE=25000

mkdir -p $OUTDIR

echo "Locating data on Google Drive ..."

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

echo "Preparing random numbers for sampling subset of data..."

SHUF_RANDOM_SOURCE=${OUTDIR}/shuf-random-source.tmp
rm -f ${SHUF_RANDOM_SOURCE}
for COUNTER in {1..20625} ; do  # emirically found required size +10% safety
    echo "${COUNTER}:${SHUF_RANDOM_SEED}" | \
        sha512sum | cut -c-128 | \
        xxd -r -p >> ${SHUF_RANDOM_SOURCE}
done

echo "Downloading data from Google Drive ..."

rclone cat \
    "${THEME_A_DCU}/Irish_Data/ForasNaGaeilge/9MqDsdf834ms2NfS8L2joi7u_NCIv2.vert" \
    --bwlimit 1000M --transfers 1 | \
    scripts/extract_text_from_nci_vert.py | \
    shuf --random-source=${SHUF_RANDOM_SOURCE} | \
    tail -n ${SAMPLE_SIZE} | \
    bzip2 > ${OUTDIR}/sample-${SAMPLE_SIZE}.txt.bz2

rm -f ${SHUF_RANDOM_SOURCE}

echo "Done"

