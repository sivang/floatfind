#!/usr/bin/env python
# Copyright (C) 2005-2006 Sivan Greenberg. <sivan@ubuntu.com>
# 
# This software is distributed under the terms and conditions of the GNU General
# Public License. See http://www.gnu.org/copyleft/gpl.html for details.
import os
import sys
import pwd
import re
import fsMisc
import apt_pkg
from download import download
import apt_inst
import glob
import shutil

def inList(val,list):
	try:
		list.index(val)
	except:
		return False
	else:
		return True

def isBIN(path, arch=None):
	# print path
	cmdstr = "file '%s' | grep ELF" % path
	put, get = os.popen4(cmdstr)
	output = get.readlines()
	if output:
		return True
	else:
		return False
def isAR(path):
	cmdstr = "file '" + path + "' | grep 'current ar archive'"
        put, get = os.popen4(cmdstr)                                                                                                             
	output = get.readlines()
	if output:
		# print "* %s is an AR archive file." % path
		return True
	else:
		return False

def arExtractArchive(filename):
	print "* Extracting %s to %s." % (filename, os.getcwd())
        cmdstr = "ar -x " + filename
	put, get = os.popen4(cmdstr) 
	output = get.readlines()
	print output


def hasfloat(path,insideFileSupport=False):
	usesFloat = False
	if os.path.exists('/usr/bin/mipsel-linux-gnu-objdump'):
		prog = 'mipsel-linux-gnu-objdump'
	else:
		prog = 'objdump'
	if insideFileSupport and isAR(path):
		print "* Need to look inside ", path
		searchpath = arExtract(path)
		filelist = glob.glob(searchpath + "/*")
		for f in filelist:
			print "* Checking inside %s: %s" % (path, f)
			cmdstr = "%s -d %s | grep '$f'" % (prog, f)
			put, get = os.popen4(cmdstr)
			output = get.readlines()
			if len(output) > 0:
				usesFloat = True
			else:
				usesFloat = False
		shutil.rmtree(searchpath)
		return usesFloat
	else:
		cmdstr = "%s -d '%s' | grep '$f'" % (prog, path)                                                                                                   
		put, get = os.popen4(cmdstr)
		output = get.readlines()
		if len(output) > 0:
			return True
		else:
			return False

def findPackageByPath(path):
	cmdstr = "dpkg -S %s" % path
	put, get = os.popen4(cmdstr)
	returnList = []
	output = get.readlines()
	for line in output:
		data = line.split(':')
		data = [i.strip() for i in data]
		if data[1].find("not found")!=-1:
			data[0] = "UNKNOWN"
			data[1] = path
		returnList.append((data[0],data[1]))
	return returnList

class BinFilesByArch(list):
    def __init__(self,dirname):
    	self.size = 0
	self.dirname = dirname
	self.append(self.dirname)

    def findFiles(self,arch=None):
        for root, dirs, files in os.walk(self[0]):
            for f in files:
                path = os.path.join(root, f)
                if os.path.isfile(path):
			self.currentFile = path
			if isBIN(self.currentFile) or isAR(self.currentFile):
				if hasfloat(self.currentFile):
					self.append(self.currentFile)
	self.remove(self.dirname)


class PkgList(list):
	def __init__(self, files=None):
		self.pkglist = []
		self.filelist = files
	def preparePkgListFromFileList(self):
		for f in self.filelist:
			pkglistperfile = findPackageByPath(f)
			for pk in pkglistperfile:
				print "Package: %s  File: %s" % (pk[0],pk[1])
				if not inList(pk[0],self.pkglist):
					self.pkglist.append(pk[0])
					self.append(pk)

def pkgnameFromPath(path):
	temp = path.split('/')
	filename = temp[-1]
	pkgname = filename[:-4]
	return pkgname


def downloadPkgAndExtract(url):
	extractPath = None
	pkgname = None
	pkgf = None
	cwd = None
	pkgname = pkgnameFromPath(url)
	cwd = os.getcwd()
	extractPath = cwd + "/.floatfind/" #  + pkgname + "/"
	fsMisc.ensure_path(True,extractPath)
	os.chdir(extractPath)
	download(url)
	extractPath = debExtract(extractPath + pkgname + ".deb")
	os.chdir(cwd) # go back to the orig dir to not create dirs inside dirs
	return extractPath

def debExtract(filename,tempdir=None):
#	print "debExtract:: filename = ",filename
	dirname = pkgnameFromPath(filename)
	cwd = os.getcwd()
	if tempdir:
#		print "* tempdir specified ", tempdir
		fsMisc.ensure_path(True,tempdir)
#		print "* changing dir to ", tempdir
		os.chdir(tempdir)
	print "* Creating dir ",dirname
	os.mkdir(dirname)
	print "* Changing dir to",dirname
	os.chdir(dirname)
	pkgdir = os.getcwd()                                                                                                                                
	# pkgf = file(cwd+"/"+filename)
	pkgf = file(filename)
	# print "trying to extract ",cwd+"/"+filename
#	print "* trying to extract ", filename
	apt_inst.debExtractArchive(pkgf)
	os.chdir(cwd)
	return pkgdir # returning the path where we extracted

def arExtract(filename, tempdir=None):
	# print "arExtract:: filename = ", filename
	dirname = "ARextracted"
	cwd = os.getcwd()
	if tempdir:
		# print "* tempdir specified ", tempdir
		fsMisc.ensure_path(True,tempdir)
		# print "* changing dir to ", tempdir
		os.chdir(tempdir)
	print "* Creating dir ",dirname
	os.mkdir(dirname)
	print "* Changing dir to ",dirname
	os.chdir(dirname)
	ardir = os.getcwd()
	arExtractArchive(filename)
	os.chdir(cwd)
	return ardir
	

	



def pkgUsesFloat(path):
	print "pkgUsesFloat:: checking ",path
	pkgfloatfiles = BinFilesByArch(path)
	pkgfloatfiles.findFiles()
	if len(pkgfloatfiles) > 0:
		for i in pkgfloatfiles:
			print i,' USES FLOAT'
		return True
	else:
		return False

