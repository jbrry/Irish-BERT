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
import os
import re
import sys
import unicodedata


def print_usage():
    print('Usage: %s [options] < in.txt > out.txt' %(os.path.split(sys.argv[0])[-1]))
    print("""
Options:

    --newline               Add empty line after processing an input line

    --simple                Select basic algorithm used in November 2020

    --verbose               Add line numbers and empty lines to output

    --debug                 Add step-by-step debugging output

""")


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
    #     and find best split point
    best_split = None
    if debug:
        print('Scanning for split points...')
    count = 0
    for match in candidate_sep_re.finditer(line):
        count += 1
        punctuation = match.group(1)  # first parenthesised subgroup
        left_half_without_punct = line[:match.start()]
        if debug:
            print('split point', count)
            print('lhwp: %r, punct: %r' %(left_half_without_punct, punctuation))
        if punctuation == '.':
            last_token = left_half_without_punct.split()[-1]
            if last_token in ('DR', 'Prof', 'nDr'):
                # reject split point
                if debug:
                    print('rejected due to last token', last_token)
                continue
        left_half = line[:match.end()].rstrip()
        right_half = line[match.end():]
        if debug:
            print('halves (%d, %d): %r + %r' %(
                len(left_half), len(right_half), left_half, right_half
            ))
        # reject if a half does not contain any letters
        # (this covers cases where the left half is only a decimal number)
        if not contains_letter(left_half) \
        or not contains_letter(right_half):
            if debug:
                print('rejected as at least one half has no letters')
            continue
        # reject if the first letter of the right half is a lowercase letter
        if get_first_letter_category(right_half) == 'Ll':
            if debug:
                print('rejected as the right half\'s first letter is lowercase')
            continue
        # reject if the left half only contains a Roman number
        # (in addition to the full-stop)
        candidate_number = left_half_without_punct.strip().upper()
        if candidate_number in roman_numbers:
            if debug:
                print('rejected as left half is a Roman number')
            continue
        # prefer a split point balancing the lengths of the halves
        balance = abs(len(left_half) - len(right_half))
        candidate_split = (balance, left_half, right_half)
        if best_split is None \
        or candidate_split < best_split:
            best_split = candidate_split
    # recursion ends if there is no split point
    if best_split is None:
        if debug:
            print('no split point found')
        return [line]
    # (2) find best split point
    balance, left_half, right_half = best_split
    if debug:
        print('Best balance', balance)
    # resursively split each half
    return split_line(left_half, debug) + split_line(right_half, debug)


def main():
    opt_help    = False
    opt_simple  = False
    opt_newline = False
    opt_debug   = False
    opt_verbose = False
    while len(sys.argv) >= 2 and sys.argv[1][:1] == '-':
        option = sys.argv[1]
        option = option.replace('_', '-')
        del sys.argv[1]
        if option in ('--help', '-h'):
            opt_help = True
            break
        elif option in ('--simple', '--november-2020'):
            opt_simple = True
        elif option == '--newline':
            opt_newline = True
        elif option == '--debug':
            opt_debug = True
        elif option == '--verbose':
            opt_verbose = True
        else:
            print('Unsupported option %s' %option)
            opt_help = True
            break
    if len(sys.argv) != 1:
        opt_help = True
    if opt_help:
        print_usage()
        sys.exit(0)
    in_count = 0
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        in_count += 1
        if opt_debug or opt_verbose:
            print('<', in_count)
            print(line.rstrip())
            print()
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
            splits = split_line(line.rstrip(), debug = opt_debug)
            number_of_splits = len(splits)
            if opt_debug:
                print()
            for new_line in splits:
                out_count += 1
                if opt_debug or opt_verbose:
                    print('> %d/%d' %(out_count, number_of_splits))
                print(new_line)
                if opt_debug or opt_verbose:
                    print()
        if opt_debug or opt_verbose or opt_newline:
            print()

if __name__ == '__main__':
    main()

