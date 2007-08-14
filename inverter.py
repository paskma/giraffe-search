import re

splitter = re.compile(r"[/ \&\+,\-_\.=]")

def normalize(doc):
	words = splitter.split(doc)
	result = []
	for w in words:
		if len(w) > 0:
			result.append(w.lower())
	
	return result

def add(i, doc, dict):
	words = normalize(doc)
	
	for w in words:
		try:
			ids = dict[w]
			
			if not i in ids:
				ids.append(i)
			
		except KeyError:
			dict[w] = [i]

def invert(docs):
	"inverts list of docs into index dictionary"
	index = {}
	for i in range(len(docs)):
		add(i, docs[i], index)
	
	#for k in index.keys():
	#	index[k].sort()
	
	return index

if __name__ == "__main__":
	print splitter.split("ahoj/vole/blekota jekota&aa+bb,ccc-ddd__eee.fff=ggg")
	print splitter.split("../tmp/rmitest/Bar.Java")
