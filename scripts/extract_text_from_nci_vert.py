#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# (C) 2020 Dublin City University
# All rights reserved. This material may not be
# reproduced, displayed, modified or distributed without the express prior
# written permission of the copyright holder.

# Author: Joachim Wagner

import sys
import xml.etree.ElementTree

line_no = 0
byte_offset = 0

empty_line_after_sentence = False
empty_line_after_document = True

print_title = True
print_author = True

num_amp_tokens = '38 60 147 148 205 218 225 233 237 243 250'.split()

def print_sentence(list_of_tokens):
    text = ' '.join(list_of_tokens)
    if not text or text.isspace():
        sys.sdterr.write('Empty sentence with non-empty list of tokens.\n')
        return
    amp_replacement = False
    first = True
    while first or modified:
        backup = text
        if '&quot;' in text:
            text = text.replace('&quot;',  '"')
            #text = '@@amp.quot: ' + text
        for token, char in [
            ('lt',  '<'),
            ('gt',  '>'),
            ('amp', '&'),
            ('quot', '"'),
            # apos not observed
        ]:
            source = '& %s ;' %token
            if source in text:
                text = text.replace(source,  char)
                #text = '@@amp_%s: %s' %(token, text)
        for token in num_amp_tokens:
            source = '& #%s ;' %token
            if source in text:
                text = text.replace(source, unichr(int(token)).encode('utf-8'))
                #text = '@@amp#%s: %s' %(token, text)
        modified = backup != text
        if modified:
            amp_replacement = True
        # add code here for other types of replacements not involing ampersands
        first = False
    #if amp_replacement:
    #    text = '@@amp: ' + text
    print text

sentence = []
while True:
    line_no += 1
    line = sys.stdin.readline()
    if not line:
        if sentence:
            print_sentence(sentence)
        #print '@@EOF'
        break
    try:
        line.decode('UTF-8')
        valid_utf8 = True
    except:
        sys.stderr.write('UTF-8 error in line %d at 0x0%X: %r\n' %(line_no, byte_offset, line))
        valid_utf8 = False
    byte_offset += len(line)
    if line.startswith('<'):
        if sentence:
            print_sentence(sentence)
            sentence = []
            if empty_line_after_sentence:
                print
            elif empty_line_after_document and line.startswith('</doc>'):
                print
        if line.startswith('<doc') and (print_title or print_author) and valid_utf8:
            line = line.rstrip()
            #print line
            if ' & ' in line:
                sys.stderr.write('Found ` & ` in xml tag. Escaping it as ` &amp; `: %s\n' %line)
                line = line.replace(' & ', ' &amp; ')
            doc_attributes = xml.etree.ElementTree.fromstring(
                '<?xml version="1.0" encoding="utf-8"?>%s</doc>' %line
            ).attrib
            #print '@@attributes = ', doc_attributes
            if print_title and 'title' in doc_attributes:
                #print '@@title = ', doc_attributes['title'].encode('utf-8')
                print doc_attributes['title'].encode('utf-8')
                if empty_line_after_sentence:
                    print
            if print_author and 'author' in doc_attributes:
                #print '@@author = ', doc_attributes['author'].encode('utf-8')
                print doc_attributes['author'].encode('utf-8')
                if empty_line_after_sentence:
                    print
        if line.startswith('<g'):
            # glue tag or some other unsupported tag
            raise NotImplementedError
    else:
        sentence.append(line.split()[0])

#print '@@EOL'
