#!/usr/bin/env python

import apt
import apt_inst
import os
from webglobe import URLRepo
from fileutil import *

INSTALLED_LIST = "installed.list"
DEFAULT_MIRROR = "http://ftp.uk.debian.org/debian/"
#DEFAULT_MIRROR = "http://il.archive.ubuntu.com/ubuntu/"

file_download_list = []
need_rebuild_with_soft = []

if __name__=="__main__":
	"""
	This utility expects a file named 'installed.list' that can possibly be created by:
		 $ dpkg -l | cut -d" " -f3 > installed.list
	and then sequentially processes this list, downloading package files as neccessary of the DEFAULT_MIRROR, respectively checking
	each package if it contains hard-float instructions, if so the package is added to a list that is printed when the script finishes
	This can be used to find out which packages needs a rebuild in an installed system.

	The script is fairely verbose and its output can serve as a log file for operations being taken to devise the result list.
	"""
	ifile = file(INSTALLED_LIST)
	pkg_list = ifile.readlines()
	pkg_list = [p.strip() for p in pkg_list]
	print "* Considering package list:"
	print pkg_list
	for s in pkg_list:
		print "* Considering ",s," for download."

	print "* Accessing local cache"
	localCache = apt.Cache()
	for p in pkg_list:
			print "Processing: ",p
			try:
				thispkg = localCache[p]
				sourcename = thispkg.sourcePackageName
			except:
				print "WARNING: %s was not found in package cache." % p
			else:
				candRecord = thispkg.candidateRecord
				if candRecord != None:
					try:
						Filename = candRecord['Filename']
						file_download_list.append((DEFAULT_MIRROR+Filename, sourcename))
						print "URL Added:",DEFAULT_MIRROR+Filename
					except KeyError:
						print "WARNING: %s does not seem to have a filename entry in candidate record." % p
				else:
					print "WARNING: %s does not have a candidate record." 


	for pkgtpl in file_download_list:
		pkgpath = None
		pkgpath = downloadPkgAndExtract(pkgtpl[0]) # get the complete URL from the tuple
		print "* Downloading: ",pkgpath
		if pkgpath: # if we managed to download the package file
			if pkgUsesFloat(pkgpath):
				need_rebuild_with_soft.append(pkgtpl[1])
		else:
			print "WARNING: Package %s failed to download." % pkgpath
			

	print "---------------------------------------------"
	print "Packages that need a rebuild with soft float:"
	print "---------------------------------------------"
	print need_rebuild_with_soft

