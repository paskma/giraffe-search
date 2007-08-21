import os, stat, types

path_separator = os.path.normcase('/');

def walktree(topdir):
	try:
		names = os.listdir(topdir)
		for name in names:
			full = os.path.join(topdir, name)
			
			st = os.lstat(full)
			if stat.S_ISDIR(st.st_mode):
				yield full + path_separator #mark dirs by final slash
				print "Diving into", full
				for i in walktree(full):
					yield i
			else:
				yield full
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
