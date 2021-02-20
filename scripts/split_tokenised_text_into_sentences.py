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
import math
import os
import re
import sys
import unicodedata


def print_usage():
    print('Usage: %s [options] < in.txt > out.txt' %(os.path.split(sys.argv[0])[-1]))
    print("""
Options:

    --newline               Add empty line after processing an input line
                            (specify twice to also add a newline after
                            every new sentence boundary)

    --simple                Select basic algorithm used in November 2020

    --verbose               Add line numbers and empty lines to output

    --wrap  NUMBER          Warp output at NUMBER characters. Does not apply
                            to debugging output. (Default: no wrapping)

    --debug                 Add step-by-step debugging output

    --help                  Show this message
""")


candidate_sep_re = re.compile(' ([.?!]) ')

closing_brackets = set(')]}>')

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

def get_first_letter_category(s, skip_enumeration = False):
    if skip_enumeration:
        new_tokens = []
        for token in s.split():
            if token.startswith('(') \
            and token.endswith(')') \
            and ((len(token) == 3 \
            and unicodedata.category(token[1]).startswith('L')) \
            or token[1:-1].upper() in roman_numbers):
                # Roman number in brackets or single letter in brackets
                # --> remove first token
                pass
            else:
                new_tokens.append(token)
        s = ' '.join(new_tokens)
    for c in s:
        category = unicodedata.category(c)
        if category.startswith('L'):
            return category
    return None

def contains_letter(s):
    return get_first_letter_category(s) is not None

def is_decimal_number(s):
    s = s.strip()
    for c in s:
        if c not in '0123456789':
            return False
    if s.startswith('0') and len(s) > 1:
        return False
    return len(s) > 0

def is_quote(token):
    if token in ("''", "``", "`", "'", '"'):
        return True
    if len(token) != 1:
        return False
    try:
        name = unicodedata.name(token)
    except:
        return False
    return 'QUOTATION MARK' in name

def is_ellipsis(s):
    if s.count('.') < 2:
        return False
    for c in s:
        if not is_quote(c) and not c in '. ':
            return False
    return True

def check_split(best_split, left_half, right_half, left_half_without_punct, debug, bonus):
    if debug:
        print('halves (%d, %d): %r + %r' %(
            len(left_half), len(right_half), left_half, right_half
        ))
    # reject if a half does not contain any letters
    # (this covers cases where the left half is only a decimal number)
    tokens = left_half.split()
    n_left = len(tokens)
    if not contains_letter(left_half) \
    and (n_left <= 2 or (tokens[-3] in "#'" and is_decimal_number(tokens[-2]))):
        if debug:
            print('rejected as left half has no letters and is short')
        return best_split
    if not contains_letter(right_half) \
    and (len(right_half.split()) < 3 \
    or is_ellipsis(right_half)):
        if debug:
            print('rejected as right half has no letters and is short or is an ellipsis')
        return best_split
    # reject if the first letter of the right half is a lowercase letter
    if get_first_letter_category(right_half, skip_enumeration = True) == 'Ll':
        if debug:
            print('rejected as the right half\'s first letter, skipping enumerations, is lowercase')
        return best_split
    # reject if the left half only contains a Roman number
    # (in addition to the full-stop)
    candidate_number = left_half_without_punct.strip().upper()
    if candidate_number in roman_numbers:
        if debug:
            print('rejected as left half is a Roman number')
        return best_split
    # reject if inside brackets and brackets not far away
    for obr, cbr in [
        ('(', ')'),
        ('[', ']'),
        ('{', '}'),
        ('<', '>'),
    ]:
        opened_at = left_half.rfind(obr)
        if opened_at < 0 or left_half.rfind(cbr) > opened_at:
            continue
        text_after_bracket = left_half[opened_at+1:]
        opened_at = right_half.find(obr)
        if opened_at < 0:
            opened_at = len(right_half)
        closed_at = right_half.find(cbr)
        if closed_at < 0 or opened_at < closed_at:
            continue
        if 3 + text_after_bracket.count(' ') + \
           right_half[:closed_at].count(' ') > 20:
            continue
        if debug:
            print('rejected as inside brackets %r and %r' %(obr, cbr))
        return best_split
    # prefer a split point balancing the lengths of the halves
    balance = abs(len(left_half) - len(right_half))
    score   = balance - bonus
    if debug:
        print('Candidate score %d with balance %d' %(score, balance))
    candidate_split = (score, balance, left_half, right_half)
    if best_split is None \
    or candidate_split < best_split:
        best_split = candidate_split
    return best_split

def split_line(line, debug = False, is_left_most = True):
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
        right_half = line[match.end():]
        if debug:
            print('split point', count)
            print('lhwp: %r, punct: %r' %(left_half_without_punct, punctuation))
        bonus = 0
        tokens = left_half_without_punct.split()
        rtokens = right_half.split()
        if len(rtokens) > 2 \
        and ((is_quote(rtokens[0]) and is_quote(rtokens[1])) \
        or (rtokens[0] == ')' and tokens and tokens[0] == '(') \
        or (rtokens[0] == ']' and tokens and tokens[0] == '[') \
        or (rtokens[0] == '}' and tokens and tokens[0] == '{') \
        or (rtokens[0] == '>' and tokens and tokens[0] == '<') \
        or (rtokens[0] in '?!' and rtokens[0] == punctuation)):
            # consider splitting between the quotes
            # (or after the closing bracket or repeated question or
            # exclamation marks) with higher priority
            n = 1
            while rtokens[0] in '?!' and rtokens[0] == punctuation \
            and len(rtokens) > n and rtokens[n] == punctuation:
                n = n + 1
            left_half2 = '%s %s %s' %(left_half_without_punct, punctuation, ' '.join(rtokens[:n]))
            best_split = check_split(
                best_split,
                left_half2,
                ' '.join(rtokens[n:]),
                left_half_without_punct,
                debug,
                5
            )
        if rtokens[0] in closing_brackets:
            # do not split at punctuation followed by a closing bracket,
            # except when promoted above
            continue
        if punctuation == '.':
            try:
                last_token = tokens[-1]
            except IndexError:
                last_token = None
            if is_left_most and count == 1 and last_token == '1' \
            and len(tokens) > 1 and tokens[-2] not in ',;':
                # candidate for start of an enumeration following a heading
                left_half2 = ' '.join(tokens[:-1])
                best_split = check_split(
                    best_split, left_half2,
                    '%s . %s' %(last_token, line[match.end():]),
                    left_half2, debug,
                    10
                )
            if last_token in ('DR', 'Prof', 'nDr'):
                # reject split point
                if debug:
                    print('rejected due to last token', last_token)
                continue
            if last_token in ('No', 'Vol', 'Iml') \
            and rtokens \
            and is_decimal_number(rtokens[0][0]):
                if debug:
                    print('rejected due to last token', last_token,
                          'followed by number', rtokens[0]
                    )
                continue
            if is_decimal_number(last_token):
                # smaller positive numbers are more likely to be part of an enumeration
                dec_number = int(last_token.strip())
                if dec_number >= 1:
                    bonus = -30 / math.log(1.0 + dec_number)
                if len(tokens) > 2 and tokens[-2].endswith('.') \
                and tokens[-3] in ('Airteagal', ) \
                and len(rtokens) > 2 and is_decimal_number(rtokens[0]) \
                and rtokens[1] == '.' \
                and get_first_letter_category(right_half) != 'Ll':
                    #        [-3]      [-2] [-1] punct
                    # ... in Airteagal  K.  16    .    4 . Beidh feidhm ...
                    bonus = 8
        left_half = line[:match.end()].rstrip()
        best_split = check_split(
            best_split, left_half, right_half, left_half_without_punct, debug,
            bonus,
        )
    # recursion ends if there is no split point
    if best_split is None:
        if debug:
            print('no split point found')
        return [line]
    # (2) find best split point
    score, balance, left_half, right_half = best_split
    if debug:
        print('Best score %d with balance %d' %(score, balance))
    # resursively split each half
    return split_line(left_half,  debug, is_left_most) + \
           split_line(right_half, debug, False)

def print_line(line, wrap):
    if not wrap:
        print(line)
    on_this_line = 0
    tokens = []
    for token in line.split():
        needed_space = len(token)
        if tokens:
            needed_space += 1
        if on_this_line + needed_space > wrap:
            # cannot fit this token on the current line
            if tokens:
                print(' '.join(tokens))
            tokens = []
            on_this_line = 0
        tokens.append(token)
        on_this_line += needed_space
    if tokens:
        print(' '.join(tokens))

def main():
    opt_help    = False
    opt_simple  = False
    opt_newline = 0
    opt_debug   = False
    opt_verbose = False
    opt_wrap    = 0
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
            opt_newline += 1
        elif option == '--wrap':
            opt_wrap = int(sys.argv[1])
            del sys.argv[1]
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
            print_line(line.rstrip(), opt_wrap)
            print()
        if opt_simple:
            for sep in ('.', '?', '!'):
                # scan for `sep` surrounded by spaces and
                # replace 2nd space with line break
                # (occurrences attach to or inside a token
                # are not touched)
                line = line.replace(' %s ' %sep, ' %s\n' %sep)
            print_line(line.rstrip(), opt_wrap)
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
                print_line(new_line, opt_wrap)
                if opt_debug or opt_verbose or opt_newline == 2:
                    print()
        if opt_debug or opt_verbose or opt_newline == 1:
            print()

if __name__ == '__main__':
    main()

