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
# cat Irish_Data/DGT/DGT_all2015-17.ga | ~/bert/Irish-BERT/scripts/display_character_frequencies.py | less

max_stars = 7

char2freq = collections.defaultdict(lambda: 0)

while True:
    line = sys.stdin.readline()
    if not line:
        break
    for char in line:
        codepoint = ord(char)
        char2freq[codepoint] += 1

max_freq = 0
for k, v in char2freq.items():
    if v > max_freq:
        max_freq = v

codepoints = sorted(list(char2freq.keys()))

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
    row.append(category)
    row.append(name)
    print('\t'.join(row))
    
