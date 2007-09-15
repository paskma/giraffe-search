import os, stat, types, sys

path_separator = os.path.normcase('/');
fs_encoding = sys.getfilesystemencoding()

def norm_enc(filename):
    "normalizes encoding to utf8"
    if fs_encoding == "UTF-8":
        return filename
    else:
        u = unicode(filename, fs_encoding)
        return u.encode("UTF-8")

def walktree(topdir):
	try:
		names = os.listdir(topdir)
		for name in names:
			full = os.path.join(topdir, name)
			
			st = os.lstat(full)
			if stat.S_ISDIR(st.st_mode):
				yield norm_enc(full + path_separator) #mark dirs by final slash
				print "Diving into", full
				for i in walktree(full):
					yield norm_enc(i)
			else:
				yield norm_enc(full)
	except OSError, er:
		print "warn", er

def fulltree(topdir):
	return [i for i in walktree(topdir)]
	

if __name__ == "__main__":
	#print fulltree("../tmp")
	#x = "../tmp";
	x = "/"
	for i in walktree(x):
		print i
