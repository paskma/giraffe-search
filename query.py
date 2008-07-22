#!/usr/bin/env python
import makeindex, inverter, lister
from bisect import bisect_left

def intersection(a, b):
	return list(set(a).intersection(set(b)))

def difference(a,b):
	return list(set(a).difference(set(b)))

def union(a,b):
	return list(set(a).union(set(b)))

def multion(lists):
	result = set();
	
	for lst in lists:
		for i in lst:
			result.add(i)
	
	return list(result)


def test_multion():
	result = multion([[1,5,6],[4,5,6,],[70],[3],[3],[]])
	result.sort()
	assert result == [1, 3, 4, 5, 6, 70]
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
	query_info = []
	
	# all breeds of yes words
	firstrun = True

	for w in words:
		next = []
		if w in wild_words:
			to_multion = []
			for i in sorted_words:
				if i.startswith(w):
					to_multion.append(index[i])

			next = multion(to_multion);
			query_info.append((w+'*', len(next)))
		elif w in strict_words:
			try: next = index[w]
			except KeyError: next = []
			query_info.append((w+'&', len(next)))
		else: #non-strict yes-word
			i = bisect_left(sorted_words, w)
			
			if i < len(sorted_words) and sorted_words[i].startswith(w): #possible match
				if sorted_words[i] != w: #not exact match
					
					#find the most popular
					SEARCH_AREA = 200
					for j in xrange(i, i+SEARCH_AREA):
						if j < len(sorted_words) and sorted_words[j].startswith(w):
							if len(index[sorted_words[j]]) > len(index[sorted_words[i]]):
								i = j #j is more popular than i
						else:
							break
				
					#print "ENHACED", sorted_words[i]
					next = index[sorted_words[i]]
					query_info.append((w+"~"+sorted_words[i][len(w):], len(next)))
				else: #exact matcho
					next = index[sorted_words[i]]
					query_info.append((w, len(next)))
			else:
				next = []
				query_info.append((w, 0))
			
		if firstrun:
			firstrun = False
			ids = next
		else:
			ids = intersection(ids, next)
	
	#not words
	for w in not_words:
		try:
			next = index[w]
			ids = difference(ids, next)
			query_info.append(('-'+w, len(next)))
		except KeyError:
			query_info.append(('-'+w, 0))
		
	
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
	return result, query_info



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
		#test_multion()

