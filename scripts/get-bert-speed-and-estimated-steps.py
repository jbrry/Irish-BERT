#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) 2021 Dublin City University
# All rights reserved. This material may not be
# reproduced, displayed, modified or distributed without the express prior
# written permission of the copyright holder.

# Author: Joachim Wagner

from __future__ import print_function

import os
import sys
import time

limit = 3600.0 * float(sys.argv[1])
folder = sys.argv[2]

step2time = {}
start = None
for entry in os.listdir(folder):
    if entry == 'graph.pbtxt':
        start = os.path.getmtime(folder + '/' + entry)
    elif entry.startswith('model.ckpt-') \
    and entry.endswith('.index'):
        step = int(entry.replace('-', '.').split('.')[2])
        ckpt = os.path.getmtime(folder + '/' + entry)
        step2time[step] = ckpt

if not step2time or not start:
    print('not a bert pre-training folder')
    sys.exit()

steps = list(step2time.keys())
earliest_step = min(steps)
latest_step = max(steps)

print('Step %d: %s' %(earliest_step, time.ctime(step2time[earliest_step])))
print('Step %d: %s' %(latest_step, time.ctime(step2time[latest_step])))

speed = (latest_step-earliest_step) / (step2time[latest_step]-step2time[earliest_step])

print('Current speed: %.1f steps per hour' %(3600.0*speed))

assert start is not None

spent_time = step2time[latest_step] - start

print('Run for %.1f hours so far' %(spent_time/3600.0))

print('Overall speed: %.1f steps per hour' %(3600.0*latest_step/spent_time))

remaining_time = limit - (step2time[latest_step] - start)

n_steps = latest_step + remaining_time * speed

print('Expect to reach step %.3f' %n_steps)

example_folder = """
-rw-r--r-- 1 retracted users    8618403 May 25 13:16 graph.pbtxt
-rw-r--r-- 1 retracted users 1317392156 May 27 09:55 model.ckpt-470000.data-00000-of-00001
-rw-r--r-- 1 retracted users      23350 May 27 09:55 model.ckpt-470000.index
-rw-r--r-- 1 retracted users    3663105 May 27 09:55 model.ckpt-470000.meta
-rw-r--r-- 1 retracted users 1317392156 May 27 10:00 model.ckpt-471000.data-00000-of-00001
-rw-r--r-- 1 retracted users      23350 May 27 10:00 model.ckpt-471000.index
-rw-r--r-- 1 retracted users    3663105 May 27 10:00 model.ckpt-471000.meta
-rw-r--r-- 1 retracted users 1317392156 May 27 10:06 model.ckpt-472000.data-00000-of-00001
-rw-r--r-- 1 retracted users      23350 May 27 10:06 model.ckpt-472000.index
-rw-r--r-- 1 retracted users    3663105 May 27 10:06 model.ckpt-472000.meta
-rw-r--r-- 1 retracted users 1317392156 May 27 10:12 model.ckpt-473000.data-00000-of-00001
-rw-r--r-- 1 retracted users      23350 May 27 10:12 model.ckpt-473000.index
-rw-r--r-- 1 retracted users    3663105 May 27 10:12 model.ckpt-473000.meta
-rw-r--r-- 1 retracted users 1317392156 May 27 10:17 model.ckpt-474000.data-00000-of-00001
-rw-r--r-- 1 retracted users      23350 May 27 10:17 model.ckpt-474000.index
-rw-r--r-- 1 retracted users        283 May 27 10:17 checkpoint
-rw-r--r-- 1 retracted users    3663105 May 27 10:17 model.ckpt-474000.meta
-rw-r--r-- 1 retracted users   63678179 May 27 10:19 events.out.tfevents.16219449
"""

