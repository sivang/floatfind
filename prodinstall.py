#!/usr/bin/python

import apt
import os

DEBS_DIR = "/home/sivan/target/debs/"

def calculatePkgsToInstall():
	"""
	This will check which of the currently installed packages have a ready soft-float version in the DEBS_DIR
	"""
	cache = apt.Cache()
	for p in cache.keys():
		pkg = cache[p]
		print p
		if pkg.isInstalled:
			instRecord = pkg.installedRecord
			filename = instRecord['Filename']
			filename = filename.split("/")[-1]
			print "Checking if %s exists..." % (DEBS_DIR + filename)
			if os.path.exists(DEBS_DIR + filename):
				print filename," exists! that's good."

if __name__=="__main__":
	calculatePkgsToInstall()
