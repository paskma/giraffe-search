#!/usr/bin/env python
import makeindex, inverter, lister
from bisect import bisect_left

import priklad
import hello_ext

def intersection(a, b):
	return list(set(a).intersection(set(b)))

def difference(a,b):
	return list(set(a).difference(set(b)))

def union(a,b):
	#a.sort()
	#b.sort()
	return list(set(a).union(set(b)))
	#return priklad.uni(a,b)

def raw_multion(lists):
	result = []
	for i in lists:
		result = union(result, i)
	return result

def multiread(lists):
	count = 0;
	foo = 0;
	for lst in lists:
		for i in lst:
			foo += i;
			count += 1;
	
	print "pycount %s foo %s" % (count, foo)
	return []

def multiset(lists):
	result = set();
	
	for lst in lists:
		for i in lst:
			result.add(i)
	
	return list(result)

def multion(lists):
	"""union of multiple sorted lists"""
	if not lists:
		raise ValueError

	result = []
	active = list(lists)
	indices = [0] * len(active)
	
	while True:
		new_active = []
		new_indices = []
		
		for i, lst in enumerate(active):
			if indices[i] < len(lst):
				new_active.append(lst)
				new_indices.append(indices[i])
		
		active = new_active
		indices = new_indices

		if not active:
			return result
		
		mindoc = 2**64
		increment = []
		for i, lst in enumerate(active):
			doc = lst[indices[i]]
			if doc < mindoc:
				increment = [i]
				mindoc = doc
			elif doc == mindoc:
				increment.append(i)
	
		if len(result) == 0 or result[len(result)-1] != mindoc:
			result.append(mindoc)
		
		for i in increment:
			indices[i] += 1

def test_multion():
	assert multion([[1,5,6],[4,5,6,],[70],[3],[3],[]]) == [1, 3, 4, 5, 6, 70]
	print "OK"

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
			to_multion = []
			for i in sorted_words:
				if i.startswith(w):
					to_multion.append(index[i])
					#next = union(next, index[i])
			print "to union", len(to_multion)
			#next = multion(to_multion)
			#next = hello_ext.multion(to_multion)
			#next = hello_ext.multiread(to_multion)
			#next = multiread(to_multion);
			#next = multiset(to_multion);
			next = raw_multion(to_multion);
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

