#!/usr/bin/env python

import sys

lfile = sys.argv[1]

lfilecontent = file(lfile).readlines() # pkg list

for l in lfilecontent:
	print "/host/scripts/checkfloat.py ",l

