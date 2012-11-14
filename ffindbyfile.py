#!/usr/bin/env python

import os
import sys
from fileutil import BinFilesByArch, PkgList, findPackageByPath


LIST_FILE = sys.argv[1]




ffile = file(LIST_FILE)
filelist = ffile.readlines()
filelist = [p.strip() for p in filelist]

for f in filelist:
	f = f.split("File:")
	f = " ".join(f)
	f = f.split("/")
	f = [i.strip() for i in f]
	if len(f) > 2:
		file_name_comp_list = f[3:]
		temp = "/".join(file_name_comp_list)
		pkgs = findPackageByPath(temp)
		for i in pkgs:
			print "Package: %s , File: %s" % (i[0],i[1])
		

	
	
