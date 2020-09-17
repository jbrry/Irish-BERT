#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# (C) 2020 Dublin City University
# All rights reserved. This material may not be
# reproduced, displayed, modified or distributed without the express prior
# written permission of the copyright holder.

# Author: Joachim Wagner

import sys

line_no = 0
byte_offset = 0

while True:
    line_no += 1
    line = sys.stdin.readline()
    if not line:
        break
    try:
        line.decode('UTF-8')
    except:
        sys.stdout.write('error in line %d at 0x0%X: %s' %(line_no, byte_offset, line))
    if not line.endswith('\n'):
        sys.stdout.write('\n')
    byte_offset += len(line)

