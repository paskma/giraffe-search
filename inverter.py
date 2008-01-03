import re

splitter = re.compile(r"[/ \&\+,\-_\.=\[\]\(\)\\]") #() []

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
			ids.add(i)
		except KeyError:
			dict[w] = set([i])

def invert(docs):
	"inverts list of docs into index dictionary"
	index = {}
	for i in range(len(docs)):
		add(i, docs[i], index)
	
	for k in index.keys():
		foo = list(index[k])
		foo.sort()
		index[k] = foo
	
	return index

def test_splitter():
	print splitter.split("ahoj/vole/blekota jekota&aa+bb,ccc-ddd__eee.fff=ggg[hhh](iii)jjj")
	print splitter.split("../tmp/rmitest/Bar.Java")

if __name__ == "__main__":
	test_splitter()
