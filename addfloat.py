#!/usr/bin/env python

from fileutil import *
import checkfloat
import os
import sys
import apt
import floatfind
import shutil
import glob


checkfloat.REPREPRO_BASE_DIR = "/builds/myrepo" # this is because we execute this script from the build cluster, change to location of repo if moved


def addFloatPkgsToRepo(globpattern):
	""" Takes a wildcard and adds the matched files as packages to the debian repository 
	    pointed to by checkfloat.REPREPRO_BASE_DIR. Works from CWD.

	    The repository expected is a debian repository maintained and created using the reprepro tool available
	    from the debian repository.
	"""
	considerList = glob.glob(globpattern)
	considerList = [i for i in considerList if checkfloat.isDEB(i)]
	print "* Considering:"
	print "\n".join(considerList)
	for p in considerList:
		debname, ver, arch = checkfloat.getDebFileComponents(p)
		versionList = checkfloat.listDeb(debname)
		if ver in versionList:
			checkfloat.removeDeb(debname)
		checkfloat.includeDeb(p)

if __name__=="__main__":
	"""
	This script adds newly created soft-float enabled (free of hard float operations) package to a reprepro managed debian repository.
	Essentially a wrapper around the reprepro binary, make sure you point checkfloat.REPREPRO_BASE_DIR to the right location of your
	locally managed debian repository. The script can be used as follows:
		./addfloat -all : Will attempt adding all the debian packages found under the current working directory.
		./addfloat [file.deb]: add the specified package to the repository.

	Note: This script removed the same version of the package it needs to add to make sure the repository is clean of hardware floating point
	      operations when process ends.
	"""
	if len(sys.argv) < 2:
		print "Usage: addfloat.py -all | <package.deb>"
	elif sys.argv[1]=="-all":
		print "* Using glob patterns *.deb"
		addFloatPkgsToRepo('*.deb')
	elif checkfloat.isDEB(sys.argv[1]):
		print "* Adding a specific pkg:",sys.argv[1]
		addFloatPkgsToRepo(sys.argv[1])


				
		
	
