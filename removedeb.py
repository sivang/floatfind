#!/usr/bin/env python

import checkfloat
import os
import sys


checkfloat.REPREPRO_BASE_DIR = "/builds/myrepo" # this is because we execute this script from the build cluster, change to location of repo if moved

if __name__=="__main__":
	"""
	This script removed a debian package from the repository
	"""
	if len(sys.argv) < 2:
		print "Usage: removedeb.py <package.deb>"
	else:
		print "* Removing :",sys.argv[1]
		checkfloat.removeDeb(sys.argv[1])


				
		
	
