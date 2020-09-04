"""
Searches for files in Google Drive folders and places them in a 'gathered' directory.

Usage:
    find data/ga/gdrive/ -maxdepth 3 -type f | python scripts/gather_gdrive_data.py
"""

import os
import sys
import shutil

# ignore paracrawl, wikipedia and already processed files
CORPORA_TO_IGNORE = ['Paracrawl', 'Vicipeid_monolingual', 'processed_ga_files_for_BERT_runs']
en_bitext_filemarker = '.en'

lines = sys.stdin.readlines()
print(f"Found {len(lines)} input files")

destination_path="data/ga/gdrive/gathered"
if not os.path.exists(destination_path):
    print(f"Creating target directory at: {destination_path}")
    os.makedirs(destination_path)

for filepath in lines:
    # strip newline symbol from output of find command
    new_line_symbol = filepath.rfind('\n')
    filepath = filepath[:new_line_symbol]

    parts = filepath.split('/')
    path_prefix = parts[:3]
    path_suffix = parts[3:]
    
    filename = path_suffix[-1]
    
    # skip README
    if "README" in filename:
        continue
    file_type = filename[-3:]
    # rudimentary filtering to exclude the '.en' versions of bitext
    if file_type == en_bitext_filemarker:
        print("Skipping the copying of en bitext")
        continue

    # corpus is the parent folder
    corpus = path_suffix[0]
    if corpus in CORPORA_TO_IGNORE:
        print(f"Skipping {corpus}")
    else:
        destination_file = os.path.join(destination_path, filename)
        print(f"Copying file {destination_file}")
        shutil.copyfile(filepath, destination_file)
