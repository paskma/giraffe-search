#!/usr/bin/env python
import makeindex, inverter, lister

def intersection(a, b):
	#return list(set(one).intersection(set(two)))
	
	#a.sort(); b.sort()
	pointerA = 0; pointerB = 0
	la = len(a); lb = len(b)
	result = []
	while pointerA < la and pointerB < lb:
		if a[pointerA] == b[pointerB]: # If they are the same add it into a result
			result.append(a[pointerA])
			pointerA += 1
			pointerB += 1
		elif a[pointerA] < b[pointerB]:
			pointerA += 1
		else:
			pointerB += 1
			
	return result

def test_intersection():
	a = [1,2,3,3,4,5]
	b = [3,4,6,7,8]
	print a, b, intersection(a,b)

def get_docs(query, index, docs, dirs_only=False):
	#print "i,d", index, docs
	words = inverter.normalize(query)
	ids = []
	firstrun = True
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

