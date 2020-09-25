#!/bin/bash

# requires opustools https://pypi.org/project/opustools-pkg/
# pip install opustools-pkg

DOWNLOAD_DIR=data/ga/jw300/
mkdir -p $DOWNLOAD_DIR

# download data for a source and target pair and write to file
opus_read --directory JW300 --source ga --target gl --write_mode moses --write $DOWNLOAD_DIR/jw300.ga $DOWNLOAD_DIR/jw300.gl --download_dir $DOWNLOAD_DIR

