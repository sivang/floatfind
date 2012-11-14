#!/usr/bin/env python

import re
import os
import sys
import urllib2



class URLRepo:
	URL = None # holds this URL's address, as is the parent of the son URLs it will hold
	def __init__(self, URL, arch=""):
		""" A Class representing the collection of all son URLs a parent URL holds.
		URL is the internet URL to prcess."""
		self.URL = URL
		self.links = []
		self.filenames = []
		print "* Trying ", URL
		try:
			raw_html = urllib2.urlopen(URL).read() # note this completely disregards proper HTTP workflow e.g. proper GET headers
		except:
			try:
				raw_html = urllib2.urlopen(URL).read()
			except:
				raw_html = urllib2.urlopen(URL).read()
		self.html = raw_html
		linkre = re.compile('''href=\"?(.[^\"\>]*)\"?(.[^\>]*)>(.[^\<]*)</a>''',re.IGNORECASE) # match the URL and its corrsponding title
		self.links = linkre.findall(raw_html)
		if arch!="":
			self.links = [l for l in self.links if l[2].find(arch)!=-1]
		for l in self.links:
			self.filenames.append(l[0])
			








if __name__ == '__main__':
	SEED_URL = sys.argv[1]
	A = URLRepo(SEED_URL, sys.argv[2])
	print A.html
	print "List of matching files for architecture %s", sys.argv[2]
	print "---------------------------------------------"
	print A.filenames
