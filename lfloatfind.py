#!/usr/bin/env python

import os
from fileutil import BinFilesByArch, PkgList


DIRLISTFILE = "dirlist.txt"


"""
Local Float Find:

This utility expects to find a file named 'dirlist.txt' in which a list of directories is found. It will then scan each of the directories
to see of binaires found there contains hardware floating point operations and if so, will trace to which package holds this file, to eventually
create a list of 'offending' packages and 'offending' files, respectively, that need a rebuild to get rid of the offending hard-float instructions. 

The format of the 'dirlist.txt' is basically one dir per line.
"""

float_pkglist = []

dfile = file(DIRLISTFILE)
dirlist = dfile.readlines()
dirlist = [p.strip() for p in dirlist]

for d in dirlist:
	files = BinFilesByArch(d)
	files.findFiles()
	pkgs = PkgList(files)
	pkgs.preparePkgListFromFileList()

print "***** Package list: *****"
print "\n".join(pkgs.pkglist)
	
	
