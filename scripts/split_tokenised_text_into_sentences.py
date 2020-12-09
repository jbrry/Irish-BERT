#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) 2020 Dublin City University
# All rights reserved. This material may not be
# reproduced, displayed, modified or distributed without the express prior
# written permission of the copyright holder.

# Author: Joachim Wagner


'''
   input: one or more tokenised sentences per line; sentences not to cross line breaks
   output: one tokenised sentence per line
'''

import collections
import re
import sys
import unicodedata

candidate_sep_re = re.compile(' ([.?!]) ')

roman_numbers = set()

# code for wite_roman() from
# https://stackoverflow.com/questions/28777219/basic-program-to-convert-integer-to-roman-numerals
# user:2548721 NullDev "Data Aberration" https://twitter.com/nulldeviance https://github.com/jerome-montino

def write_roman(num):
    roman = collections.OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"
    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= (r * x)
            if num <= 0:
                break
    return ''.join([a for a in roman_num(num)])

for i in range(1,3000):
    roman_numbers.add(write_roman(i))

def get_first_letter_category(s):
    for c in s:
        category = unicodedata.category(c)
        if category.startswith('L'):
            return category
    return None

def contains_letter(s):
    return get_first_letter_category(s) is not None

def split_line(line, debug = False):
    global candidate_sep_re
    # (1) score each candidate split point
    candidate_split_points = []
    if debug:
        print('Scanning for split points...')
    for match in candidate_sep_re.finditer(line):
        punctuation = match.group(1)  # first parenthesised subgroup
        left_half_without_punct = line[:match.start()]
        if debug:
            print('lhwp: %r, punct: %r' %(left_half_without_punct, punctuation))
        if punctuation == '.':
            last_token = left_half_without_punct.split()[-1]
            if last_token in ('DR', 'Prof', 'nDr'):
                # reject split point
                continue
        left_half = line[:match.end()].rstrip()
        right_half = line[match.end():]
        if debug:
            print('halves (%d, %d): %r + %r' %(
                len(left_half), len(right_half), left_half, right_half
            ))
        # reject if a half does not contain any letters
        if not contains_letter(left_half) \
        or not contains_letter(right_half):
            if debug:
                print('no letters')
            continue
        # reject if the first letter of the right half is a lowercase letter
        if get_first_letter_category(right_half) == 'Ll':
            if debug:
                print('lowercase letter')
            continue
        # reject if the left half only contains a Roman number
        # (in addition to the full-stop)
        candidate_number = left_half_without_punct.strip().upper()
        if candidate_number in roman_numbers:
            if debug:
                print('Roman number')
            continue
        # prefer a split point balancing the lengths of the halves
        balance = abs(len(left_half) - len(right_half))
        candidate_split_points.append((balance, left_half, right_half))
    # recursion ends if there is no split point
    if not candidate_split_points:
        return [line]
    # (2) find best split point
    candidate_split_points.sort()
    best_split = candidate_split_points[0]
    balance, left_half, right_half = best_split
    if debug:
        print('Best balance', balance)
    # resursively split each half
    return split_line(left_half) + split_line(right_half)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--simple':
        opt_simple = True
    else:
        opt_simple = False
    in_count = 0
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        in_count += 1
        #print('Input line:', in_count)
        if opt_simple:
            for sep in ('.', '?', '!'):
                # scan for `sep` surrounded by spaces and
                # replace 2nd space with line break
                # (occurrences attach to or inside a token
                # are not touched)
                line = line.replace(' %s ' %sep, ' %s\n' %sep)
            sys.stdout.write(line)
        else:
            out_count = 0
            for new_line in split_line(line.rstrip()):
                out_count += 1
                #print('Output line:', out_count)
                sys.stdout.write(new_line)
                sys.stdout.write('\n')
                #print()

if __name__ == '__main__':
    main()

