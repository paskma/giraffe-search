#!/usr/bin/env python
import makeindex, inverter, lister

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
	for i in terms:
		normalized_term = inverter.normalize(i) #returns a list
		if i.startswith("-"):
			no_terms += normalized_term
		elif i.endswith("*"):
			wild_terms += normalized_term
		else:
			yes_terms += normalized_term
	
	return yes_terms, no_terms, wild_terms
	

def get_docs(query, index, docs, dirs_only=False):
	words, not_words, wild_words = parse_query(query)
	ids = []
	
	#wild words
	for i in index:
		for w in wild_words:
			if i.startswith(w):
				ids = union(ids, index[i])
	
	
	# normal words
	if not ids: firstrun = True
	else: firstrun = False
	
	try:
		for w in words:
			if firstrun:
				firstrun = False
				ids = index[w]
			else:
				next = index[w]
				ids = intersection(ids, next)
	except KeyError:
		ids = []
	
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
		index, docs = makeindex.readindex("index.pickle")
		docs = get_docs(' '.join(argv[1:]), index, docs) #todo normalize
		for i in docs:
			print i
	else:
		print "Usage: query.py keyword [keyword] ..."
		#test_intersection()

