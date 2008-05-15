#!/usr/bin/env python

import os
import pygtk
pygtk.require('2.0')
import gtk, gobject
import logging as log
import threading as th
import time

try:
	import iconutils
except ImportError:
	import wiconutils as iconutils

PSYCO = False
if PSYCO:
	try:
		import psyco
		psyco.full()
	except ImportError:
		log.error("Psyco not available")
	
import query, makeindex
from watches import StopWatch as W

MT = True #Multithreading
MT_INDEX = False #Loading index in worker thread (slow)

if os.name == 'nt':
	MT = False #PyGTK on win32 does not support threads

if not MT:
	MT_INDEX = False


class Data(th.Thread):
	def __init__(self, filename):
		th.Thread.__init__(self)
		if not MT_INDEX: self.load_index()
		self.cond = th.Condition()
		self.queue = []
		self.setDaemon(True)
		if MT: self.start()


	def load_index(self):
		log.info("Loading index.")
		w = W()
		self.index, self.docs, self.sorted_words = makeindex.readindex("index.pickle")
		log.info("Index loaded %s" % w)
		if MT_INDEX: self.update_logo_cb(busy=False, lock=True)
		
	def run(self, *args, **kwargs):
		assert MT
		log.debug("Daemon started")
		if MT_INDEX: self.load_index()
		while True:
			self.cond.acquire()		
			if not self.queue:
				self.cond.wait()
			query = self.queue.pop()
			self.queue = []
			self.cond.release()
			
			result = self.get_result(*query)
			
			time.sleep(0.05)
			if self.queue: continue
			
			self.view_result_cb(result)
	
	
	def get_result(self, a_query, dirs_only):
		w = W()
		result = query.get_docs(a_query, self.index, self.docs, self.sorted_words, dirs_only)
		log.debug("Query: '%s', %s docs, %s" % (a_query, len(result), w))
		return result
	
	def set_result_cb(self, cb):
		self.view_result_cb = cb
	
	def set_update_logo_cb(self, logo_cb):
		self.update_logo_cb = logo_cb
	
	def do_query(self, a_query, dirs_only):
		if MT:
			self.cond.acquire()
			self.queue.append((a_query, dirs_only))
			self.cond.notify()
			self.cond.release()
		else:
			self.view_result_cb(self.get_result(a_query, dirs_only))

class Mainform:
	"""
		THE MAIN AND ONLY FORM!
	"""

	RESULT_LIMIT = 100
	# Drag'n'Drop
	TARGET_TYPE_TEXT = 80
	TARGET_TYPE_URI = 81
	TARGETS = [('text/plain', 0, TARGET_TYPE_TEXT), ("text/uri-list", 0, TARGET_TYPE_URI)]
	

	def search(self, widget, data=None):
		w = W()
		self.update_logo(busy=True,lock=False)
		dirs_only = self.dirs_only.get_active()
		query = self.query.get_text()
		self.data.do_query(query, dirs_only)
		log.debug("Lag '%s' %s " % (query, w))
	
	def view_result(self, docs):
		"""
		   Called from Data class 
		"""
		w = W()
		if MT: gtk.gdk.threads_enter()
		dirs_only = self.dirs_only.get_active()
		self.result_store.clear()

		if self.limit_results.get_active(): 
			show_docs = docs[:self.RESULT_LIMIT]
		else:
			show_docs = docs

		self.limit_results.set_sensitive(len(docs) > self.RESULT_LIMIT)	
		
		for i in show_docs:
			#print "'%s'" % i
			self.result_store.append([iconutils.cached_icon_for_file(i, dirs_only), i])
		
		if docs: 
			self.window.set_title("Giraffe: %s (%s items found)" % (self.query.get_text(), len(docs)))
		else:
			self.window.set_title("Giraffe")
		self.update_logo(busy=False, lock=False)
		if MT: gtk.gdk.threads_leave()
		log.debug("View %s " % w)
	
	def update_logo(self, busy, lock):
		"""
			Called from Data class"
				busy - boolean, which logo
				lock - boolean, whether to lock
		"""
		if MT and lock: gtk.gdk.threads_enter()
		if busy:
			self.logo.set_from_pixbuf(self.picture_busy.get_pixbuf())
		else:
			self.logo.set_from_pixbuf(self.picture_ready.get_pixbuf())
		if MT and lock: gtk.gdk.threads_leave()
			
	def query_changed(self, widget, data=None):
		self.search(widget, data)
	
	def result_row_activated(self, treeview, path, view_column, user_param1):
		model = treeview.get_model()
		iter = model.get_iter(path)
		filename = model.get_value(iter, 1)
		if os.name == 'nt':
			import config
			os.startfile(unicode(filename, 'UTF-8').encode(config.WIN_ENC))
		else: # probably posix
			os.spawnvp(os.P_NOWAIT,"xdg-open",["",filename])


	def delete_event(self, widget, event, data=None):
		return False

	def destroy(self, widget, data=None):
		gtk.main_quit()
	
	def drag_data_get(self, treeview, context, selection, target_type, etime):
		treeselection = treeview.get_selection()
		model, iter = treeselection.get_selected()
		data = model.get_value(iter, 1)
		
		if target_type == self.TARGET_TYPE_TEXT:
			log.debug("DnD: TEXT")
			selection.set(selection.target, 8, data)
		elif target_type == self.TARGET_TYPE_URI:
			log.debug("DnD: URI")
			selection.set(selection.target, 8, data)
		else:
			log.error("UNKNOWN DnD TARGET TYPE")

	def __init__(self):
		self.data = None # will be set
		# create a new window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)
		
		#load images
		self.picture_ready = gtk.Image()
		self.picture_ready.set_from_file("giraffe-logo.png")
		self.picture_busy = gtk.Image()
		self.picture_busy.set_from_file("giraffe-logo-dark.png")
		
		try:
			self.window.set_icon_from_file("giraffe-logo.png")
		except Exception, ex:
			print ex
	
		# Sets the border width of the window.
		self.window.set_border_width(5)
		self.window.set_title("Giraffe")
		self.window.set_default_size(820, 300)
		
		self.mainbox = gtk.VBox()
		
		self.topbox = gtk.HBox()
		self.topbox.set_border_width(8)
		self.topbox.set_spacing(8)
		
		self.bottom_box = gtk.HBox()
		self.bottom_box.set_border_width(0)
		self.bottom_box.set_spacing(5)
		
		self.labelq = gtk.Label()
		self.labelq.set_text("Search:")
		self.query = gtk.Entry()
		#self.button = gtk.Button("Search")

		
		self.logo = gtk.Image()
		if MT_INDEX: self.update_logo(busy=True, lock=False)
		else: self.update_logo(busy=False, lock=False)
		
		# Results
		self.sw_result = gtk.ScrolledWindow()
		self.sw_result.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
		self.result_store = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
		self.result = gtk.TreeView(self.result_store)
		# Results - tree view
		self.result_tvcolumn = gtk.TreeViewColumn('Result')
		self.result_tvcolumn.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
		self.result.append_column(self.result_tvcolumn)
		self.result_cell_ico = gtk.CellRendererPixbuf()
		self.result_cell_text = gtk.CellRendererText()
		self.result_tvcolumn.pack_start(self.result_cell_ico, False)
		self.result_tvcolumn.pack_start(self.result_cell_text, True)
		self.result_tvcolumn.add_attribute(self.result_cell_ico, 'pixbuf', 0)
		self.result_tvcolumn.add_attribute(self.result_cell_text, 'text', 1)
		self.result.set_search_column(0)
		self.result_tvcolumn.set_sort_column_id(0)
		self.result.connect("row-activated", self.result_row_activated, None)
		# drag'n'drop support
		self.result.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, 
			self.TARGETS ,gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_COPY)
		self.result.connect("drag_data_get", self.drag_data_get)
		
		# status bar
		self.dirs_only = gtk.CheckButton("Show Directories Only")
		self.dirs_only.set_active(True)
		self.limit_results = gtk.CheckButton("Limit results to %s" % self.RESULT_LIMIT)
		self.limit_results.set_sensitive(False)
		self.limit_results.set_active(True)
	
		# signals
		self.query.connect("changed", self.query_changed, None)
		self.dirs_only.connect("clicked", self.search, None)
		self.limit_results.connect("clicked", self.search, None)
	
		# Main form assembly
		self.topbox.pack_start(self.labelq, expand=False)
		self.topbox.pack_start(self.query)
		self.topbox.pack_start(self.logo, expand=False)
		self.mainbox.pack_start(self.topbox, expand=False)
		self.sw_result.add(self.result)
		self.mainbox.pack_start(self.sw_result)
		self.bottom_box.pack_start(self.dirs_only, expand=False)
		self.bottom_box.pack_start(self.limit_results, expand=False)
		self.mainbox.pack_start(self.bottom_box, expand=False)
		self.window.add(self.mainbox)
	
		self.window.show_all()
		

	def main(self):
		gtk.gdk.threads_enter()
		gtk.main()
		gtk.gdk.threads_leave()



if __name__ == "__main__":
	dlevel = log.INFO
	dlevel = log.DEBUG
	log.basicConfig(level=dlevel,
			format='%(asctime)s %(levelname)-8s %(message)s')
	log.debug("App start." + ("" if MT else " MT disabled"))
	gtk.gdk.threads_init()
	form = Mainform()
	data = Data("index.pickle")
	data.set_result_cb(form.view_result)
	data.set_update_logo_cb(form.update_logo)
	form.data = data
	form.main()
	log.info("Done.")

