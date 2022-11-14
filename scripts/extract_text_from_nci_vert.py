#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) 2020 Dublin City University
# All rights reserved. This material may not be
# reproduced, displayed, modified or distributed without the express prior
# written permission of the copyright holder.

# Author: Joachim Wagner

import sys
import xml.etree.ElementTree
from collections import defaultdict

# defaults below can be changed with command line options

empty_line_after_sentence = False
empty_line_after_document = False
print_line_numbers = False
print_sentence_length = False    # raw length before fixing issues
print_title = False
print_author = False
count_events = False
debug_level = 1

while len(sys.argv) > 1 and sys.argv[1].startswith('--'):
    option = sys.argv[1]
    del sys.argv[1]
    if option == '--sentence-newline':
        empty_line_after_sentence = True
    elif option == '--document-newline':
        empty_line_after_document = True
    elif option in ('--line', '--line-numbers'):
        print_line_numbers = True
    elif option in ('--length', '--sentence-length'):
        print_sentence_length = True
    elif option == '--title':
        print_title = True
    elif option == '--author':
        print_author = True
    elif option == '--count-events':
        count_events = True
    elif option == '--quiet':
        debug_level = 0
    elif option == '--verbose':
        debug_level = 2
    elif option == '--debug':
        debug_level = 5
    elif option == '--debug-level':
        debug_level = int(sys.argv[1])
        del sys.argv[1]
    else:
        raise ValueError('unknown option')

event_counter = defaultdict(lambda: 0)

num_amp_tokens = '38 60 147 148 205 218 225 233 237 243 250'.split()

start_of_sentence_line = 0

def print_sentence(list_of_tokens):
    global debug_level
    global print_sentence_length
    global print_line_numbers
    global start_of_sentence_line
    global count_events
    global event_counter
    text = ' '.join(list_of_tokens)
    if not text or text.isspace():
        if debug_level >= 1:
            sys.sdterr.write('Empty sentence with non-empty list of tokens.\n')
        if count_events:
            event_counter[('text', 'empty')] += 1
        return
    amp_replacement = False
    first = True
    while first or modified:
        backup = text
        if '&quot;' in text:
            if count_events:
                event_counter[('replace', '&quot;')] += text.count('&quot;')
            text = text.replace('&quot;',  '"')
            if debug_level >= 5:
                text = '@@amp.quot: ' + text
        for token, char in [
            ('lt',  '<'),
            ('gt',  '>'),
            ('amp', '&'),
            ('quot', '"'),
            # apos not observed
        ]:
            source = '& %s ;' %token
            if source in text:
                if count_events:
                    event_counter[('replace', source)] += text.count(source)
                text = text.replace(source,  char)
                if debug_level >= 5:
                    text = '@@amp_%s: %s' %(token, text)
        for token in num_amp_tokens:
            source = '& #%s ;' %token
            if source in text:
                if count_events:
                    event_counter[('replace', source)] += text.count(source)
                text = text.replace(source, chr(int(token)))
                if debug_level >= 5:
                    text = '@@amp_#%s: %s' %(token, text)
        modified = backup != text
        if modified:
            amp_replacement = True
        # add code here for other types of replacements not involing ampersands
        first = False
    if count_events and modified:
        event_counter[('text', 'modified segment')] += 1
    if amp_replacement and debug_level >= 5:
        text = '@@amp: ' + text
    if print_line_numbers:
        text = '%d\t%s' %(start_of_sentence_line, text)
    if print_sentence_length:
        text = '%d\t%s' %(len(list_of_tokens), text)
    print(text)

line_no = 0
byte_offset = 0
sentence = []
while True:
    line_no += 1
    line = sys.stdin.buffer.readline()
    if not line:
        if sentence:
            print_sentence(sentence)
            if count_events:
                event_counter[('text', 'segment')] += 1
        if debug_level >= 4:
            print('@@EOF')
        break
    try:
        line.decode('UTF-8', 'strict')
        valid_utf8 = True
        if count_events:
            event_counter[('line', 'valid utf-8')] += 1
    except:
        if debug_level >= 1:
            sys.stderr.write('UTF-8 error in line %d at 0x0%X: %r\n' %(line_no, byte_offset, line))
        valid_utf8 = False
        if count_events:
            event_counter[('line', 'invalid utf-8')] += 1
    byte_offset += len(line)
    line = line.decode('UTF-8', 'ignore')   # skip bytes that cannot be decoded
    if line.startswith('<'):
        if count_events:
            event_counter[('tag', line.split()[0])] += 1
        if sentence:
            print_sentence(sentence)
            sentence = []
            if empty_line_after_sentence:
                print()
        if empty_line_after_document and line.startswith('</doc>'):
            print()
        if line.startswith('<doc') and (print_title or print_author) and valid_utf8:
            line = line.rstrip()
            if debug_level >= 4:
                print(line)
            if ' & ' in line:
                if debug_level >= 2:
                    sys.stderr.write('Found ` & ` in xml tag. Escaping it as ` &amp; `: %s\n' %line)
                if count_events:
                    event_counter[('tag', 'fix &')] += line.count(' & ')
                line = line.replace(' & ', ' &amp; ')
            doc_attributes = xml.etree.ElementTree.fromstring(
                '<?xml version="1.0" encoding="utf-8"?>%s</doc>' %line
            ).attrib
            if debug_level >= 5:
                print('@@attributes = ', doc_attributes)
            if print_title and 'title' in doc_attributes:
                if debug_level >= 5:
                    print('@@title = ', doc_attributes['title'].encode('utf-8'))
                print(doc_attributes['title'].encode('utf-8'))
                if empty_line_after_sentence:
                    print()
            if print_author and 'author' in doc_attributes:
                if debug_level >= 5:
                    print('@@author = ', doc_attributes['author'].encode('utf-8'))
                print(doc_attributes['author'].encode('utf-8'))
                if empty_line_after_sentence:
                    print()
        if line.startswith('<g'):
            # glue tag or some other unsupported tag
            raise NotImplementedError
    else:
        if not sentence:
            start_of_sentence_line = line_no
            if count_events:
                event_counter[('text', 'first token')] += 1
        sentence.append(line.rstrip().split('\t')[0])
        if count_events:
            event_counter[('text', 'input row')] += 1

if debug_level >= 5:
    print('@@EOL')

if count_events:
    for key in sorted(event_counter.keys()):
        print(key, event_counter[key])


