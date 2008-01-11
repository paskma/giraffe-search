#!/usr/bin/env python

import query, makeindex, inverter, lister

index, docs = makeindex.readindex("index.pickle")

resolved = {}

for doc in docs:
	filename = doc[doc.rfind(lister.path_separator)+1:]
	
	if filename in resolved:
		continue
	else:
		resolved[filename] = True
	
	found = query.get_docs(filename, index, docs)

	dups = []
	for i in found:
		if i.endswith(filename):
			dups.append(i)
	
	if len(dups) > 1:
		print filename, len(dups)

