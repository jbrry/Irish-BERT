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

import sys

while True:
    line = sys.stdin.readline()
    if not line:
        break
    for sep in ('.', '?', '!'):
        # scan for `sep` surrounded by spaces and
        # replace 2nd space with line break
        # (occurrences attach to or inside a token
        # are not touched)
        line = line.replace(' %s ' %sep, ' %s\n' %sep)
    sys.stdout.write(line)

