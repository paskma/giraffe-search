#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

import query, makeindex, inverter

class Data:
	def __init__(self, filename):
		print "Loading index"
		self.index, self.docs = makeindex.readindex("index.pickle")
	
	def get_result(self, a_query, dirs_only):
		return query.get_docs(a_query, self.index, self.docs, dirs_only)
		

class Mainform:

    RESULT_LIMIT = 100
    
    # This is a callback function. The data arguments are ignored
    # in this example. More on callbacks below.
    def search(self, widget, data=None):
    	
        self.result_store.clear()
        docs = self.data.get_result(self.query.get_text(), self.dirs_only.get_active())

        if self.limit_results.get_active(): 
            show_docs = docs[:self.RESULT_LIMIT]
        else:
            show_docs = docs

        self.limit_results.set_sensitive(len(docs) > self.RESULT_LIMIT)	
        
        for i in show_docs:
            #print "'%s'" % i
            self.result_store.append([i])
        
        if docs: 
        	self.window.set_title("Giraffe: %s (%s item(s) found)" % (self.query.get_text(), len(docs)))
        else:
        	self.window.set_title("Giraffe")
    
    def query_changed(self, widget, data=None):
    	self.search(widget, data)
    
    def result_row_activated(self, treeview, path, view_column, user_param1):
    	print "ACTIVATE start"
    	model = treeview.get_model()
        iter = model.get_iter(path)
        filename = model.get_value(iter, 0)
        import os
        if os.name == 'nt':
            import config
            os.startfile(unicode(filename, 'UTF-8').encode(config.WIN_ENC))
        else: # probably posix
            os.spawnvp(os.P_NOWAIT,"xdg-open",["",filename])
        print "ACTIVATED", filename


    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

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
        self.window.set_default_size(700, 300)
        
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
        self.result_store = gtk.ListStore(str)
        self.result = gtk.TreeView(self.result_store)
        
        
        self.result_tvcolumn = gtk.TreeViewColumn('Result')
        self.result.append_column(self.result_tvcolumn)
        self.result_cell = gtk.CellRendererText()
        self.result_tvcolumn.pack_start(self.result_cell, True)
        self.result_tvcolumn.add_attribute(self.result_cell, 'text', 0)
        self.result.set_search_column(0)
        self.result_tvcolumn.set_sort_column_id(0)
        self.result.connect("row-activated", self.result_row_activated, None)
        
   
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
        gtk.main()


if __name__ == "__main__":
    data = Data("index.pickle")
    form = Mainform(data)
    form.main()

