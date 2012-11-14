#!/usr/bin/env python

import sys

lfile = sys.argv[1]
rfile = sys.argv[2]

lfilecontent = file(lfile).readlines() # deboostrap created pkg list output
rfilecontent = file(rfile).readlines() # lfloatfind created pkg list report
resultlist = []


added = []

temp = lfilecontent[0]
temp = temp.split(" ")
temp = [i.strip() for i in temp]
lpkglist = temp
rpkglist = [i.strip() for i in rfilecontent]

for i in lpkglist:
	try:
		rpkglist.index(i)

	except:
		pass
	else:
		try:
			added.index(i)
		except:
			resultlist.append(i)
			added.append(i)

print "\n".join(resultlist)

