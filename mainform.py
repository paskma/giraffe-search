#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk, gobject
import logging as log
import threading as th

try:
    import iconutils
except ImportError:
    import wiconutils as iconutils
    
import query, makeindex, inverter
from watches import StopWatch as W

log.basicConfig(level=log.DEBUG,
                format='%(asctime)s %(levelname)-8s %(message)s')
gtk.gdk.threads_init()

class Data(th.Thread):
	def __init__(self, filename):
		th.Thread.__init__(self)
		self.load_index()
		self.cond = th.Condition()
		self.queue = []
		self.setDaemon(True)
		self.start()


	def load_index(self):
		log.info("Loading index.")
		w = W()
		self.index, self.docs = makeindex.readindex("index.pickle")
		log.info("Index loaded %s" % w)
		
	def run(self, *args, **kwargs):
		log.debug("Daemon started")
		#self.load_index()
		while True:
			self.cond.acquire()
			self.cond.wait()
			while self.queue:
				query = self.queue.pop(0)
				result = self.get_result(*query)
				self.view_result_cb(result)
			self.cond.release()
	
	def get_result(self, a_query, dirs_only):
		w = W()
		result = query.get_docs(a_query, self.index, self.docs, dirs_only)
		log.debug("Query: '%s', %s docs, %s" % (a_query, len(result), w))
		return result
	
	def set_result_cb(self, cb):
		self.view_result_cb = cb
	
	def do_query(self, a_query, dirs_only):
		self.cond.acquire()
		self.queue.append((a_query, dirs_only))
		self.cond.notify()
		self.cond.release()
	

class Mainform:

    RESULT_LIMIT = 100
    TARGET_TYPE_TEXT = 80
    TARGET_TYPE_URI = 81
    TARGETS = [('text/plain', 0, TARGET_TYPE_TEXT), ("text/uri-list", 0, TARGET_TYPE_URI)]
    

    def search(self, widget, data=None):
        #w = W()
        dirs_only = self.dirs_only.get_active()
        self.data.do_query(self.query.get_text(), dirs_only)
        #log.debug("Lag %s " % w)
    
    def view_result(self, docs):
        """
           Called from Data class 
        """
        w = W()
        gtk.gdk.threads_enter()
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
        gtk.gdk.threads_leave()
        log.debug("View %s " % w)
    
    def query_changed(self, widget, data=None):
    	self.search(widget, data)
    
    def result_row_activated(self, treeview, path, view_column, user_param1):
    	model = treeview.get_model()
        iter = model.get_iter(path)
        filename = model.get_value(iter, 1)
        import os
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
    	#print "DDG", selection
    	
    	treeselection = treeview.get_selection()
        model, iter = treeselection.get_selected()
        data = model.get_value(iter, 1)
        print data
    	
    	if target_type == self.TARGET_TYPE_TEXT:
    		#print "TEXT"
    		selection.set(selection.target, 8, data)
    	elif target_type == self.TARGET_TYPE_URI:
    		#print "URI"
    		selection.set(selection.target, 8, data)
    	else:
    		print "UNKNOWN DnD TARGET TYPE"

    def __init__(self, data):
    	self.data = data
        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        try:
        	self.window.set_icon_from_file("giraffe-ico.png")
        except Exception, ex:
        	print ex
    
        # Sets the border width of the window.
        self.window.set_border_width(5)
        self.window.set_title("Giraffe")
        self.window.set_default_size(820, 300)
        
        self.mainbox = gtk.VBox()
        
        self.topbox = gtk.HBox()
        self.topbox.set_border_width(5)
        self.topbox.set_spacing(5)
        
        self.bottom_box = gtk.HBox()
        self.bottom_box.set_border_width(0)
        self.bottom_box.set_spacing(5)
        
        self.labelq = gtk.Label()
        self.labelq.set_text("Query:")
        self.query = gtk.Entry()
        #self.button = gtk.Button("Search")
        
        self.sw_result = gtk.ScrolledWindow()
        self.sw_result.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.result_store = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
        self.result = gtk.TreeView(self.result_store)
        
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
        
   
        self.dirs_only = gtk.CheckButton("Show Directories Only")
        self.dirs_only.set_active(True)
        self.limit_results = gtk.CheckButton("Limit results to %s" % self.RESULT_LIMIT)
        self.limit_results.set_sensitive(False)
        self.limit_results.set_active(True)
    
        # When the button receives the "clicked" signal, it will call the
        # function ...() passing it None as its argument.
        #self.button.connect("clicked", self.search, None)
        self.query.connect("changed", self.query_changed, None)
        self.dirs_only.connect("clicked", self.search, None)
        self.limit_results.connect("clicked", self.search, None)
    
        # This will cause the window to be destroyed by calling
        # gtk_widget_destroy(window) when "clicked".  Again, the destroy
        # signal could come from here, or the window manager.
        #self.button.connect_object("clicked", gtk.Widget.destroy, self.window)
    
        # This packs the button into the window (a GTK container).
        self.topbox.pack_start(self.labelq, expand=False)
        self.topbox.pack_start(self.query)
        #self.topbox.pack_start(self.button, expand=False)
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
    log.debug("App start.")
    data = Data("index.pickle")
    form = Mainform(data)
    data.set_result_cb(form.view_result)
    form.main()
    log.debug("App end.")

