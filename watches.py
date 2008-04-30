from time import time as now

class StopWatch:
	def __init__(self):
		self.start = now()
	
	def stop(self):
		self.end = now()
	
	def __str__(self):
		try:
			end = self.end
		except AttributeError:
			end = now()

		return  "%.3fs" % (end - self.start)

