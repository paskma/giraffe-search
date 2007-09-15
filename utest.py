# coding=UTF-8
s = "Marek Paška"

print s
f = open(s, "wb")
f.write(s)
f.close()
print "saved"

f = open(s, "r")
x = f.read()
print "read"
print x

