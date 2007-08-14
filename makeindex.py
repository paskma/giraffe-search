#!/usr/bin/env python

import cPickle as pickle, inverter, lister

def makeindex(topdirs, filename):
	docs = []
	for i in topdirs:
		docs += lister.fulltree(i)
	print "Inverting..."
	index = inverter.invert(docs)
	output = open(filename, "wb")
	pickle.dump(index, output)
	pickle.dump(docs, output)
	output.close()

def readindex(filename):
	data = open(filename, "rb")
	index = pickle.load(data)
	docs = pickle.load(data)
	print "Docs:", len(docs), "words:", len(index)
	return index, docs

if __name__ == "__main__":
	from sys import argv
	if len(argv) >= 2:
		makeindex(argv[1:], "index.pickle")
		print "Done."
	else:
		print "Usage: makeindex.py DIR [DIR] ..."
		
