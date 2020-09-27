"""
Move files selected for processing to the 'raw' sub-folder

Usage:
    find data/ga/gdrive/ -maxdepth 3 -type f | python3 scripts/gather_gdrive_data_by_filelist.py
"""
import os
import sys
import shutil
import subprocess
import csv

FILE_LIST = "data/ga/gdrive/gdrive_filelist.csv"

def get_file_list(filename):
    """Return a List of files to be processed"""
    with open(filename, newline='') as csvfile:
        files=[]
        filereader = csv.reader(csvfile, delimiter=',')
        for row in filereader:
            if row[0].lstrip()[0] != '#':   #ignore comments in csv file
                files.append(row)
    return files


def split_file_list(file_list):
    """Return 3 lists of include_files, exclude_files, and exception_files"""
    include_files=[]
    exclude_files=[]
    exception_files=[]
    for file in file_list:
        if file[0] == "1":
            include_files.append(file[1])
        elif file[0] == '0':
            exclude_files.append(file[1])
        else:
            exception_files.append(file)
    return include_files, exclude_files, exception_files


def copy_selected_files(include_files, local_files):
    print("Copying files")
    destination_path = "data/ga/gdrive/raw"
    if not os.path.exists(destination_path):
        print(f"Creating target directory at: {destination_path}")
        os.makedirs(destination_path)

    for filepath in local_files:
        # strip newline symbol from output of find command
        new_line_symbol = filepath.rfind('\n')
        filepath = filepath[:new_line_symbol]
        head_tail = os.path.split(filepath)
        filename = head_tail[1]
        if filepath in include_files:
            destination_file = os.path.join(destination_path, filename)
            print(f"Copying file {destination_file}")
            shutil.copyfile(filepath, destination_file)
        else:
            print("Skipping {}".format(filepath))

    # compress all files
    print(f"Compressing files in {destination_path}")
    subprocess.call(f'bzip2 {destination_path}/*', shell=True)
    print("Finished compressing files")


if __name__ == '__main__':
    print('Starting.')
    if not os.path.isfile(FILE_LIST):
        print("Please retrieve the filelist using ./scripts/download_gdrive_filelist.sh")
        exit('Error: {} not found'.format(FILE_LIST))

    file_list = get_file_list(FILE_LIST)
    include_files, exclude_files, exception_files = split_file_list(file_list)
#    print("include files ({})\n{}".format(len(include_files), include_files))
#    print("exclude files ({})\n{}".format(len(exclude_files), exclude_files))
#    print("exception files ({})\n{}".format(len(exception_files), exception_files))

    local_files = sys.stdin.readlines()
    print("Found {} input files".format(len(local_files)))
    copy_selected_files(include_files, local_files)

    print('Finished.')