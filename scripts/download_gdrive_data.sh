#!/bin/bash

# downloads files from Google Drive using rclone

# use double-quotes if the path contains spaces
rclone copy "gdrive:Theme A DCU/Irish_Data/" data/ga_sample/gdrive --bwlimit 1M --transfers 1

