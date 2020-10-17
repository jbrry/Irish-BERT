#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# (C) 2020 Dublin City University
# All rights reserved. This material may not be
# reproduced, displayed, modified or distributed without the express prior
# written permission of the copyright holder.

# Author: Joachim Wagner

import hashlib
import math
import os
import random
import sys
import struct
import sys
import time
import zlib

def print_usage():
    print 'Usage: %s [options] input1.txt input2.txt output.png' %(sys.argv[0].split('/')[-1])

opt_help = False
opt_debug = False
opt_max_box_size       = 800
opt_margin             = 6
opt_dither             = True        # use dithering to exceed png's 8-bit colour precision
opt_preview            = False       # write preview pictures (unfinished lines are transparent)
opt_num_preview        = 2           # limit the number of preview pictures available at any time
opt_clean_up_preview   = True
opt_force_overwrite    = False
opt_progress_interval  = 1.0

while len(sys.argv) >= 2 and sys.argv[1][:1] == '-':
    option = sys.argv[1]
    del sys.argv[1]
    if option in ('--help', '-h'):
        opt_help = True
        break
    elif option == '--debug':
        opt_debug = True
    elif option in ('--size', '--max-box-size'):
        opt_max_box_size = int(sys.argv[1])
        del sys.argv[1]
    elif option == '--margin':
        opt_margin = int(sys.argv[1])
        del sys.argv[1]
    elif option == '--force-overwrite':
        opt_force_overwrite = True
    elif option == '--dither':
        opt_dither = True
    elif option == '--preview':
        opt_preview = True
    elif option in ('--previews', '--number-of-previews'):
        opt_num_preview = int(sys.argv[1])
        del sys.argv[1]
    elif option in ('--keep-previews', '--do-not-clean-up'):
        opt_clean_up_preview = False
    elif option == '--progress-interval':
        opt_progress_interval = float(sys.argv[1])
        del sys.argv[1]
    else:
        print 'Unsupported option %s' %option
        opt_help = True
        break

if len(sys.argv) != 4:
    opt_help = True

if opt_help:
    print_usage()
    sys.exit(0)

colours = {
    'black':     (0.00, 0.00, 0.00),
    'white':     (1.00, 1.00, 1.00),
    'dark_blue': (0.00, 0.00, 0.35),
}

in1 = open(sys.argv[1], 'rb')
in2 = open(sys.argv[2], 'rb')
outname = sys.argv[3]

if os.path.exists(outname) and not opt_force_overwrite:
    sys.stderr.write('Refusing to overwrite %s. Remove it first or use --force-overwrite to replace it.\n' %outname)
    sys.exit(1)

lines1 = in1.readlines()
lines2 = in2.readlines()
in1.close()
in2.close()

if opt_debug:
    print('number of lines:', len(lines1), len(lines2))

n_lines_1 = len(lines1)
n_lines_2 = len(lines2)
max_buckets_1 = n_lines_1 // 3   # cannot form line triplets with more buckets
max_buckets_2 = n_lines_2 // 3

max_buckets_1 = min(max_buckets_1, opt_max_box_size)   # user-specific maximum size
max_buckets_2 = min(max_buckets_2, opt_max_box_size)   # user-specific maximum size

scale1 = n_lines_1 / float(max_buckets_1)
scale2 = n_lines_2 / float(max_buckets_2)
scale = max(scale1, scale2)

n_buckets_1 = int(n_lines_1 / scale)
n_buckets_2 = int(n_lines_2 / scale)

if opt_debug:
    print('number of buckets:', n_buckets_1, n_buckets_2)

assert n_buckets_1 > 0
assert n_buckets_2 > 0

width = n_buckets_1 + 2 * opt_margin
height = n_buckets_2 + 2 * opt_margin

# png writing code adapted from
# http://stackoverflow.com/questions/902761/saving-a-numpy-array-as-an-image

raw_data = []
transparent = b'\x00\x00\x00\x00'
line = width * transparent
for i in range(height):
    raw_data.append(b'\x00' + line)

def png_pack(png_tag, data):
    chunk_head = png_tag + data
    return (struct.pack("!I", len(data)) +
            chunk_head +
            struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk_head)))

def write_png(filename):
    global raw_data
    global width
    global height
    out = open(filename, 'wb')
    out.write(b'\x89PNG\r\n\x1a\n')
    out.write(png_pack(b'IHDR', struct.pack("!2I5B", width, height, 8, 6, 0, 0, 0)))
    png_data = b''.join(raw_data)
    out.write(png_pack(b'IDAT', zlib.compress(png_data, 9)))
    out.write(png_pack(b'IEND', b''))
    out.close()

def replace_png_line(line, row_index):
    global raw_data
    data = b'\x00' + line
    raw_data[row_index] = data

def dither_and_pack(colour, x, y):
    global opt_dither
    retval = []
    for cvalue in colour:
        if opt_dither:
            cvalue = int(1020.99 * cvalue)
            bvalue = cvalue // 4
            pattern = cvalue % 4
            if pattern > 0:
                xo = x % 2
                yo = y % 2
                if pattern == 1 and xo == 0 and yo == 0:
                    bvalue += 1
                elif pattern == 2 and xo == yo:
                    bvalue += 1
                elif pattern == 3 and (xo == 1 or yo == 0):
                    bvalue += 1
            cvalue = bvalue
        else:
            cvalue = int(255.99 * cvalue)
        if cvalue < 0 or cvalue > 255:
            cvalue = 96 + int(64*random.random())
        retval.append(chr(cvalue))
    retval.append(chr(255))   # opaque
    return b''.join(retval)

def get_buckets(lines, number_of_buckets, info = '?'):
    global opt_debug
    remaining_lines = len(lines)
    remaining_buckets = number_of_buckets
    retval = []
    index = 0
    last_verbose = 0.0
    start_t = time.time()
    while remaining_buckets:
        if time.time() > last_verbose + opt_progress_interval:
            sys.stderr.write('%s: %d buckets remaining. %.1f%% done.  \r' %(
                info,
                remaining_buckets,
                100.0 * (number_of_buckets-remaining_buckets)/float(number_of_buckets)
            ))
            last_verbose = time.time()
        bucket_channel_1 = set()
        bucket_channel_2 = set()
        bucket_channel_3 = set()
        lines_for_this_bucket = remaining_lines // remaining_buckets
        previous_lines = []
        for _ in range(lines_for_this_bucket):
            line = lines[index]
            # bucket channel 1: lines without whitespace
            line_without_whitespace = ''.join(line.split())
            bucket_channel_1.add(line_without_whitespace)
            # bucket channel 2: hash of triplets of lines
            previous_lines.append(line.strip())
            if len(previous_lines) == 3:
                text = '\n'.join(previous_lines)
                sha256 = hashlib.sha256(text).digest()
                bucket_channel_2.add(sha256)
                del previous_lines[0]
            # bucket channel 3: token trigrams
            tokens = line.split()
            previous_tokens = []
            for token in tokens:
                previous_tokens.append(token)
                if len(previous_tokens) == 3:
                    text = ' '.join(previous_tokens)
                    bucket_channel_3.add(text)
                    del previous_tokens[0]
            index = index + 1
        retval.append((bucket_channel_1, bucket_channel_2, bucket_channel_3))
        remaining_lines = remaining_lines - lines_for_this_bucket
        remaining_buckets = remaining_buckets - 1
    if last_verbose:
        duration = time.time()-start_t
        sys.stderr.write('%s: Prepared all buckets in %.1fs.       \n' %(
            info, duration,
        ))
    return retval
        
buckets_1 = get_buckets(lines1, n_buckets_1, 'File 1')
lines1 = None

buckets_2 = get_buckets(lines2, n_buckets_2, 'File 2')
lines2 = None

def get_colour_for_pixel(x, y):
    global buckets_1
    global buckets_2
    global n_buckets_1
    global n_buckets_2
    global colours
    global opt_margin
    if x >= opt_margin and y >= opt_margin:
        # alignment box
        bucket_index_1 = x - opt_margin
        bucket_index_2 = y - opt_margin
        if bucket_index_1 >= n_buckets_1 \
        or bucket_index_2 >= n_buckets_2:
            return colours['white']
        colour = []
        for channel_index in range(3):
            bucket_1 = buckets_1[bucket_index_1][channel_index]
            bucket_2 = buckets_2[bucket_index_2][channel_index]
            max_overlap_possible = min(len(bucket_1), len(bucket_2))
            actual_overlap = len(bucket_1 & bucket_2)
            try:
                fraction = actual_overlap / float(max_overlap_possible)
                colour.append(0.95 - 0.95 * fraction)
            except ZeroDivisionError:
                colour.append(1.00)
        return colour
    if False:
        # TODO: projection bars
        if x >= opt_margin and y < opt_margin//2:
            bucket_index_1 = x - opt_margin
            if bucket_index_1 >= n_buckets_1:
                return colours['white']
            raise NotImplementedError
        if y >= opt_margin and x < opt_margin//2:
            bucket_index_2 = y - opt_margin
            if bucket_index_2 >= n_buckets_2:
                return colours['white']
            raise NotImplementedError
    return colours['white']

startt = time.time()
last_verbose = 0.0
last_preview = 0.0
preview_threshold = 20.0
preview_index = 0
preview_lastnames = []

shuffleindex = list(range(height))
random.shuffle(shuffleindex)
for s_index in range(height):
    y = shuffleindex[s_index]
    line = []
    start_this_line = time.time()
    for x in range(width):
        colour = get_colour_for_pixel(x,y)
        line.append(dither_and_pack(colour, x, y))
    line = b''.join(line)
    replace_png_line(line, y)
    remaining = height - 1 - y
    now = time.time()
    if not remaining:
        eta = now
    else:
        eta = now + (now-start_this_line) * remaining
    now = time.time()
    if now > last_verbose + opt_progress_interval:
        info = []
        percentage = 100.0 * (1.0+s_index) / float(height)
        info.append('Line %d (%.1f%%)' %(s_index+1, percentage))
        elapsed = now - startt
        if elapsed < 100.0:
            info.append('elapsed %.1f seconds' %elapsed)
        elif elapsed < 6000.0:
            info.append('elapsed %.1f minutes' %(elapsed/60.0))
        elif elapsed < 50.0*3600.0:
            info.append('elapsed %.1f hours' %(elapsed/3600.0))
        else:
            info.append('elapsed %.1f days' %(elapsed/3600.0/24.0))
        remaining = height - 1 - s_index
        if not remaining:
            eta = now
        else:
            eta = now + (now-start_this_line) * remaining
        info.append('ETA = %s' %time.ctime(eta))
        sys.stderr.write(', '.join(info))
        sys.stderr.write('  \r')
        last_verbose = now

    if opt_preview and now > last_preview + preview_threshold \
    and s_index < height - 1:
        # write preview picture
        last_slash = outname.rfind('/')
        if last_slash >= 0:
            preview_name = '%s/preview-%s-%03d.png' %(
                outname[:last_slash],
                outname[last_slash+1:-4],
                preview_index
            )
        else:
            preview_name = 'preview-%s-%03d.png' %(outname[:-4], preview_index)
        write_png(preview_name)
        preview_lastnames.append(preview_name)
        while len(preview_lastnames) > opt_num_preview:
            # delete previous preview picture
            if os.path.exists(preview_lastnames[0]):
                os.unlink(preview_lastnames[0])
            del preview_lastnames[0]
        preview_threshold *= 1.414
        last_preview = now
        preview_index += 1

now = time.time()
duration = now - startt
sys.stderr.write('\nPrepared lines in %.1f seconds.\n' %duration)
sys.stderr.write('\n\nWriting PNG file\n\n')

write_png(outname)

if opt_clean_up_preview:
    # delete preview picture(s)
    for preview_name in preview_lastnames:
        if os.path.exists(preview_name):
            os.unlink(preview_name)

sys.stderr.write('Finished ' + time.ctime(time.time())+'\n')


