#!/bin/bash

IRISH_OSCAR_UNSHUFFLED="https://oscar-public.huma-num.fr/f1f454290e16df612b59e17154d8725a61f42d02/unshuffled/ga.txt.gz" # you need to contact OSCAR maintainers for un-shuffled version
OUTDIR=data/ga/oscar/raw

# download handle for UDPipe v2.5 Irish model
UDPIPE_ga="https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/irish-idt-ud-2.5-191206.udpipe?sequence=39&isAllowed=y"
UDPIPE_MODEL_DIR=udpipe_models

# Download UDPipe
if [ -s "$UDPIPE_MODEL_DIR" ]; then
    echo "$UDPIPE_MODEL_DIR exists, skipping download." >&2
else
    mkdir -p ${UDPIPE_MODEL_DIR}
    echo $'\n'"Downloading UDPipe model for ga..."$'\n'
    curl ${UDPIPE_ga} -o ga.udpipe
    mv ga.udpipe ${UDPIPE_MODEL_DIR}
fi  

# Download Oscar corpus
if [ -s "$OUTDIR" ]; then
    echo "$OUTDIR exists, skipping download." >&2
else
    mkdir -p ${OUTDIR}
    echo $'\n'"Downloading Oscar data for ga..."$'\n'
    cd $OUTDIR
    wget $IRISH_OSCAR_UNSHUFFLED
fi  


