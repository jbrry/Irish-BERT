"""
Searches for files in Google Drive folders and places them in a 'gathered' directory.

Usage:
    find data/ga/gdrive/ -maxdepth 3 -type f | python scripts/gather_gdrive_data.py
"""

import os
import sys
import shutil
import subprocess

# ignore paracrawl, wikipedia and already processed files
CORPORA_TO_IGNORE = ['Paracrawl', 'Vicipeid_monolingual', 'processed_ga_files_for_BERT_runs']
FILES_TO_IGNORE = ['AnnualReport2011b.docx.txt.sent', 'CKDublinCity1steditb.docx.txt.sent', 'CollectionDevelopmentPolicy_EN.txt.sent', 'DCHG_everything.en.txt.anon', 'DUCoLAnnualReport2014_EN.txt.sent', 'gaois.en.txt', 'Library_guidelines_adult_EN.txt.sent', 'MembershipApplicationForm2016Final.txt.sent', 'Metadata.xlsx', 'new_brochure.txt.sent', 'PictureParnellSqaurePressrelease.txt.sent', 'Textforboard1.txt.sent', 'Textforboard2.txt.sent', 'Textforboard3.txt.sent', 'Textforboard4.txt.sent', 'Textforboard5.txt.sent', 'Textforboard6.txt.sent', 'Textforboard7.txt.sent', 'UnescoOnlineProjetCriteriab.txt.sent', 'unicode-errors.docx']
en_bitext_filemarker = '.en'

lines = sys.stdin.readlines()
print(f"Found {len(lines)} input files")

destination_path="data/ga/gdrive/raw"
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
    
    # corpus is the parent folder
    corpus = path_suffix[0]
    if corpus in CORPORA_TO_IGNORE:
        print(f"Skipping {corpus}")
        continue

    # skip certain en/metadata files
    if filename in FILES_TO_IGNORE:
        print(f"Ignoring {filename}")
        continue

    if "README" in filename:
        continue

    file_type = filename[-3:]
    # rudimentary filtering to exclude the '.en' versions of bitext
    if file_type == en_bitext_filemarker:
        print("Skipping the copying of en bitext")
        continue

    destination_file = os.path.join(destination_path, filename)
    print(f"Copying file {destination_file}")
    shutil.copyfile(filepath, destination_file)

# compress all files
print(f"Compressing files in {destination_path}")
subprocess.call(f'bzip2 {destination_path}/*', shell=True)
print("Finished compressing files")

