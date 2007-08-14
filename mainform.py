#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

import query, makeindex, inverter

class Data:
	def __init__(self, filename):
		print "Loading index"
		self.index, self.docs = makeindex.readindex("index.pickle")
	
	def get_result(self, a_query):
		return query.get_docs(a_query, self.index, self.docs)
		

class Mainform:

    # This is a callback function. The data arguments are ignored
    # in this example. More on callbacks below.
    def search(self, widget, data=None):
    	self.window.set_title("Giraffe: " + self.query.get_text())
    	
    	self.result.get_buffer().set_text("")
    	docs = self.data.get_result(self.query.get_text())
    	for i in docs:
    		self.result.get_buffer().insert_at_cursor(i+"\r\n")
    
    def query_changed(self, widget, data=None):
    	self.search(widget, data)

    def delete_event(self, widget, event, data=None):
        # If you return FALSE in the "delete_event" signal handler,
        # GTK will emit the "destroy" signal. Returning TRUE means
        # you don't want the window to be destroyed.
        # This is useful for popping up 'are you sure you want to quit?'
        # type dialogs.
        print "delete event occurred"

        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
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
        
        self.labelq = gtk.Label()
        self.labelq.set_text("Query:")
        self.query = gtk.Entry()
        self.button = gtk.Button("Search")
        
        self.sw_result = gtk.ScrolledWindow()
        self.sw_result.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.result = gtk.TextView()
    
        # When the button receives the "clicked" signal, it will call the
        # function ...() passing it None as its argument.
        self.button.connect("clicked", self.search, None)
        self.query.connect("changed", self.query_changed, None)
    
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
        self.mainbox.add(self.sw_result)
        self.window.add(self.mainbox)
    
        self.window.show_all()
        

    def main(self):
        gtk.main()


if __name__ == "__main__":
    data = Data("index.pickle")
    form = Mainform(data)
    form.main()

