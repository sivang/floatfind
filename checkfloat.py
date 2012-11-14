#!/usr/bin/env python

from fileutil import *
import os
import sys
import apt
import floatfind
import shutil
import glob

DEBS_DIR = "/home/sivan/target/debs/"
TEMPDIR = ".checkfloat/"
STORE_PATH =  "/home/sivan/" 
REPREPRO_BASE_DIR = "/home/sivan/builds/myrepo" # this is the directory where you store youre reprepro created debian repository
						# change as neccessary.



def isDEB(filepath):
	filenamecomp = filepath.split("/")[-1]
	ext = filenamecomp[-3:]
	if ext == "deb":
		return True
	else:
		return False
def isDocDEB(filepath):
	filenamecomp = filepath.split("/")[-1]
	if filenamecomp.find("-doc")!=-1 or filenamecomp.find("doc-")!=-1:
		return True
	else:
		return False


def getDebFileComponents(debfile):
	debfile = debfile[:-4]
	#print "debfile after cut extension = %s" % debfile
	tlist = debfile.split("_")
	#print "tlist = %s" % tlist
	pname = tlist[0]
	pver  = tlist[1]
	parch = tlist[2]
	print "Name         : ",pname
	print "Version      : ",pver
	print "Architecture :", parch
	return pname, pver, parch


def allPackageMatchByName(pkgname,where): # name here includes ofcourse package 'variants' like -dev and other varying forms of dash compound name
	pkglist = glob.glob(where + pkgname + "_*")
	return pkglist

def detectRepreproError(output):
	for line in output:
		if line.find("error")!=-1 or line.find("Error")!=-1:
			print "* REPREPRO error has been detected! halting!"
			sys.exit(-1)



def removeDeb(debname):
	print "* Removing %s from the archive!" % debname
	cmdstr = "reprepro -b %s remove lenny %s" % (REPREPRO_BASE_DIR, debname)
	put, get = os.popen4(cmdstr)
	output = get.readlines()
	for line in output:
		print line
	detectRepreproError(output)

def listDeb(debname):
	resultList = []
	print "* Checking if any version(s) of %s already exists in the repository." % debname
	cmdstr = "reprepro -b %s list lenny %s" % (REPREPRO_BASE_DIR, debname)
	put, get = os.popen4(cmdstr)
	output = get.readlines()
	#for line in output:
	#	print line
	detectRepreproError(output)
	output = [i for i in output if not i.startswith('WARNING')]
	output = [i.strip() for i in output]
	output = [i.split(" ") for i in output]
	for i in output:
		resultList.append(i[2])
	print resultList
	return resultList



def includeDeb(debfilepath):
	print "* Including %s into the archive!" % debfilepath
	cmdstr = "reprepro -b %s includedeb lenny %s" % (REPREPRO_BASE_DIR, debfilepath)
	put, get = os.popen4(cmdstr)
	output = get.readlines()
	for line in output:
		print line
	detectRepreproError(output)

	

def updatePackageForFloat(debfile):
	name, ver, arch = getDebFileComponents(debfile)
	print "* Trying to find a soft float replacement..."
	pkglist = allPackageMatchByName(pkgname=name,where=DEBS_DIR)
	if pkglist:
		print "* Found packages: %s" % pkglist
		print "* So Removing:  " + name
		removeDeb(name)
		for p in pkglist:
			print "* Including: " + p + " instead."
			includeDeb(p)
	else:
		print "* No soft float alternative was found for: " + debfile + " adding to list of packages that need rebuild for soft-float."
	        outputfile = file(STORE_PATH+TEMPDIR+"sources_to_fetch.list.txt",'a')
		outputfile.writelines(name+'\n')
		outputfile.close()

			



def updatePoolForFloat(path):
	for root, dirs, files in os.walk(path):
		for f in files:
			curpath = os.path.join(root, f)
			if os.path.isfile(curpath):
				if isDEB(curpath) and not isDocDEB(curpath): # skip doc packages
					searchpath = debExtract(curpath,"/home/sivan/"+TEMPDIR)
					if pkgUsesFloat(searchpath):
						filenamecomp = curpath.split("/")[-1]
						updatePackageForFloat(filenamecomp)
					else:
						pass
					print "* Cleaning up ", searchpath
					shutil.rmtree(searchpath)


if __name__=="__main__":
	""" 
	checkfloat.py is a utility written to help manage the software floating point enabled debian repository we have
	as currently the software we develop and choose for the LX platform has to work on a FPUless MIPS cpu.

	It can be used as follows:

	./checkfloat.py -archive-update from the root directory of a debian repository , possibly created by reprepro tool.
	   	This will go over all the package in the repository and attempt to find soft-float built counterparts in
	   	DEBS_DIR. So make sure you copy *.debs you build to that location, before using checkfloat.py that way.
		It will also create a text file listing all the packages that need rebuild to make them hard-float free.
		This file can be found after and -archive-update run at STORE_PATH+TEMPDIR+"sources_to_fetch.list.txt"

	./checkfloat.py [file.deb]
		Will extract file.deb's content and test if for any binaries offending with hard float code. Once
		found will exit and report that the debian package is using hard float and needs a rebuild

	./checkfloat.py [package-name]
		Will attempt to download the named package, extract it and then check it for offending hard-float code.
		Note, that the package needs to be available from the current package cache in order to be found as this option
		uses the cached entries of the web location of a package in repository mirror pointed at by floatfind.DEFAULT_MIRROR



	"""
	print sys.argv[1]
	usefile = False
	param = sys.argv[1]

	if param=="-archive-update":
		fsMisc.ensure_path(True,STORE_PATH+TEMPDIR)
		updatePoolForFloat(os.getcwd())
		sys.exit(0)

	tmp = param.split(".")
	if tmp[-1]=="deb":
		usefile = True
	if usefile:
		debfilepath = os.getcwd() + "/" + param
		if len(param.split('/')) > 1:
			debfilepath = param
		searchpath = debExtract(debfilepath,os.getcwd() + "/" + TEMPDIR)
		if pkgUsesFloat(searchpath):
			print "* Package: %s uses floating point and thus requires rebuild." % param 
		shutil.rmtree(searchpath)
	else:
		localCache = apt.Cache()
		try:
			thispkg = localCache[param]
		except KeyError:
			print "ERROR: Could not find package %s in package cache!" % param
			sys.exit(1)
		candRecord = thispkg.candidateRecord
		if candRecord!=None:
			try:
				Filename = candRecord['Filename']
				download_url = floatfind.DEFAULT_MIRROR + Filename
			except KeyError:
				print "ERROR: %s does not seem to have a filename entry in candidate record." % param
				sys.exit(1)
		else:
			print "ERROR: %s does not have a candidate record!" % param
			sys.exit(1)
		pkgpath = downloadPkgAndExtract(download_url)
		if pkgUsesFloat(pkgpath):
			print "* %s uses floating point and thus needs a rebuild!" % download_url
		print "* Removing ",pkgpath
		shutil.rmtree(pkgpath)


				
		
	
