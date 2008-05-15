#!/usr/bin/env python
import makeindex, inverter, lister
from bisect import bisect_left

def intersection(a, b):
	return list(set(a).intersection(set(b)))

def difference(a,b):
	return list(set(a).difference(set(b)))

def union(a,b):
	return list(set(a).union(set(b)))

def test_intersection():
	a = [1,2,3,3,4,5]
	b = [3,4,6,7,8]
	print a, b, intersection(a,b)

def parse_query(query):
	terms = query.split()
	yes_terms = []
	no_terms = []
	wild_terms = []
	strict_yes_terms = []
	for i in terms:
		normalized_term = inverter.normalize(i) #returns a list
		if i.startswith("-"):
			no_terms += normalized_term
		elif i.endswith("*"):
			wild_terms += normalized_term
		elif i.endswith("&"):
			strict_yes_terms += normalized_term
		else:
			yes_terms += normalized_term
	
	return yes_terms, no_terms, wild_terms, strict_yes_terms
	

def get_docs(query, index, docs, sorted_words, dirs_only=False):
	words, not_words, wild_words, strict_words = parse_query(query)
	words += wild_words
	words += strict_words
	ids = []
	
	# all breeds of yes words
	firstrun = True

	for w in words:
		next = []
		if w in wild_words:
			for i in sorted_words:
				if i.startswith(w):
					next = union(next, index[i])
		elif w in strict_words:
			try: next = index[w]
			except KeyError: next = []
		else: #non-strict yes-word
			i = bisect_left(sorted_words, w)
			if i < len(sorted_words) and sorted_words[i].startswith(w):
				next = index[sorted_words[i]]
				if sorted_words[i] != w: print "ENHACED", sorted_words[i]
			else:
				next = []
			
		if firstrun:
			firstrun = False
			ids = next
		else:
			ids = intersection(ids, next)
	
	#not words
	for w in not_words:
		try:
			ids = difference(ids, index[w])
		except KeyError:
			pass
		
	
	result = []
	added_dirs = {}
	for i in ids:
		doc = docs[i]
		if dirs_only:
			trimmed = doc[0:doc.rfind(lister.path_separator)]
			if trimmed not in added_dirs:
				added_dirs[trimmed] = 1
				result.append(trimmed)
		else:
			result.append(doc)
	
	result.sort()
	return result



if __name__ == "__main__":
	from sys import argv
	if len(argv) >= 2:
		index, docs, sorted_words = makeindex.readindex("index.pickle")
		docs = get_docs(' '.join(argv[1:]), index, docs, sorted_words) #todo normalize
		for i in docs:
			print i
	else:
		print "Usage: query.py keyword [keyword] ..."
		#test_intersection()

