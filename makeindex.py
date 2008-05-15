#!/usr/bin/env python

import cPickle as pickle
import logging

import  inverter, lister

def makeindex(topdirs, filename):
	docs = []
	for i in topdirs:
		docs += lister.fulltree(i)
	print "Inverting "+str(len(docs))+" docs..."
	index = inverter.invert(docs)
	output = open(filename, "wb")
	pickle.dump(index, output, pickle.HIGHEST_PROTOCOL)
	pickle.dump(docs, output, pickle.HIGHEST_PROTOCOL)
	output.close()

def readindex(filename):
	data = open(filename, "rb")
	index = pickle.load(data)
	docs = pickle.load(data)
	logging.info("Docs: %s, words: %s" % (len(docs),len(index)))
	
	sorted_words = [w for w in index]
	sorted_words.sort()
	
	return index, docs, sorted_words

if __name__ == "__main__":
	from sys import argv
	if len(argv) >= 2:
		makeindex(argv[1:], "index.pickle")
		print "Done."
	else:
		print "Usage: makeindex.py DIR [DIR] ..."
		
