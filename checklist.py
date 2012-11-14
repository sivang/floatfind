#!/usr/bin/env python

from fileutil import *
import os
import sys
import apt
import floatfind
import shutil


if __name__=="__main__":
	listfilename = sys.argv[1]
	listfile = file(listfilename)
	content = listfile.readlines()
	content = [i.strip() for i in content]
	localCache = apt.Cache()
	for p in content:
		print "* Checking %s " % p
		try:
			thispkg = localCache[p]
		except KeyError:
			print "WARNING:  %s NOT_IN_CACHE!" % param
			continue
		candRecord = thispkg.candidateRecord
		if candRecord!=None:
			try:
				Filename = candRecord['Filename']
				download_url = floatfind.DEFAULT_MIRROR + Filename
			except KeyError:
				print "WARNING: %s does not seem to have a filename entry in candidate record." % param
				continue
		else:
			print "WARNING: %s does not have a candidate record!" % param
			continue
		pkgpath = downloadPkgAndExtract(download_url)
		if pkgUsesFloat(pkgpath):
			print "* %s uses floating point and thus needs a rebuild!" % download_url
			print "* Removing ",pkgpath
		shutil.rmtree(pkgpath)


				
		
	
