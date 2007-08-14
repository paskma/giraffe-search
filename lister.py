import os, stat, types

def walktree(topdir):
	try:
		names = os.listdir(topdir)
		for name in names:
			full = os.path.join(topdir, name)
			yield full
			
			st = os.lstat(full)
			if stat.S_ISDIR(st.st_mode):
				print "Diving into", full
				for i in walktree(full):
					yield i
	except OSError, er:
		print "warn", er

def fulltree(topdir):
	return [i for i in walktree(topdir)]
	

if __name__ == "__main__":
	print fulltree("../tmp")
