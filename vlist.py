#!/usr/bin/env python
"""
This script takes two file lists:
	1) A list of packages currently installed on a given system
	2) A list of packages where a preceeding v is marking that a package has been built

The script will print the resulting list of packages that are left to built derived from the list of currently installed
packages on the system. the list is printed to stdout, use redirection to send it to a file.

"""


import sys

lfile = sys.argv[1]
rfile = sys.argv[2]

lfilecontent = file(lfile).readlines() # complete package list installed on the system
rfilecontent = file(rfile).readlines() # list of packages with v's where a package has already been built
resultlist = []

vhash = {}

complete_list = [i.strip() for i in lfilecontent]
vlist = [i.strip() for i in rfilecontent]
for i in vlist:
	temp = i.split(" ")
	if len(temp) > 1:
		if i[0]=='v':
			vhash[temp[1]]=True
		else:
			vhash[temp[1]]=False
	else:
		vhash[temp[0]]=False

for i in complete_list:
	if vhash.has_key(i):
		if vhash[i]:
			print "v",i
		else:
			print i
	else:
		print i






