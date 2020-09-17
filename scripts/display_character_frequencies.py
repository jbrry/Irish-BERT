#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (C) 2020 Dublin City University
# All rights reserved. This material may not be
# reproduced, displayed, modified or distributed without the express prior
# written permission of the copyright holder.

# Author: Joachim Wagner


import collections
import math
import sys
import unicodedata

# example usage:
# cat Irish_Data/*/*.txt | scripts/display_character_frequencies.py | less
# cat Irish_Data/*/*.txt | scripts/display_character_frequencies.py expected_characters.txt | less
# cat Irish_Data/*/*.txt | scripts/display_character_frequencies.py fairly_clean_data.txt 5 | less

max_stars = 7

expected_characters = None

if len(sys.argv) == 2:
    if sys.argv[1] in ('-h', '--help'):
        print('Check source code for usage')
        sys.exit()
    expected_characters = set()
    # read list of expected characters from file
    filename = sys.argv[1]
    f = open(filename, 'rt')
    while True:
        line = f.readline()
        if not line:
            break
        for char in line:
            expected_characters.add(char)
    f.close()

def get_char2freq(somefile):
    '''
        count occurrences of characters
    '''
    char2freq = collections.defaultdict(lambda: 0)
    line_no = 0
    while True:
        line_no += 1
        try:
            line = somefile.readline()
        except UnicodeDecodeError as details:
            sys.stderr.write('Skipping line %d of %r with unicode errors: %s\n' %(line_no, somefile, details))
            continue
        if not line:
            break
        for char in line:
            codepoint = ord(char)
            char2freq[codepoint] += 1
    return char2freq

if len(sys.argv) == 3:
    expected_characters = set()
    filename = sys.argv[1]
    reference_threshold = int(sys.argv[2])
    f = open(filename, 'rt')
    char2freq = get_char2freq(f)
    f.close()
    for k, v in char2freq.items():
        if v >= reference_threshold:
            expected_characters.add(chr(k))

# count occurrences of characters in stdin

char2freq = get_char2freq(sys.stdin)

# find maximum frequency to scale visual indicator

max_freq = 0
for k, v in char2freq.items():
    if v > max_freq:
        max_freq = v

# sort table by code point

codepoints = sorted(list(char2freq.keys()))

# print rows

for codepoint in codepoints:
    row = []
    freq = char2freq[codepoint]
    row.append('%d' %freq)
    log_freq = math.log(freq)/math.log(max_freq)
    #row.append('%.3f' %log_freq)
    num_stars = int((0.5+max_stars)*log_freq)
    row.append(num_stars * '*')
    #row.append('%d' %codepoint)
    row.append('U+%04X' %codepoint)
    char = chr(codepoint)
    category = unicodedata.category(char)
    # print the character, unless it would cause trouble
    if char in '\n\t':
        row.append('<ws>')
    elif char == '\u00ad':
        row.append('<s-hyp>')
    elif category == 'Cc':
        row.append('<ctrl>')
    else:
        row.append(char)
    # address holes in Python's unicode name table, see
    # https://stackoverflow.com/questions/24552786/why-doesnt-unicodedata-recognise-certain-characters
    # for more information
    if char == '\n':
        name = 'newline'
    elif char == '\t':
        name = 'tab'
    elif char == '\u0097':
        name = 'end of guarded area'
    else:
        try:
            name = unicodedata.name(char)
        except ValueError:
            name = '<?>'
    if expected_characters is not None:
        if char in expected_characters:
            row.append('normal')
        else:
            row.append('unexpec')
    row.append(category)
    row.append(name)
    print('\t'.join(row))
    
