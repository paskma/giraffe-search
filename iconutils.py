import gtk.gdk
import gnome.ui
import lister


ICON_THEME = gtk.icon_theme_get_default()
ICON_HEIGHT = 24
factory = gnome.ui.ThumbnailFactory(ICON_HEIGHT)

slash = lister.path_separator
icon_cache = {}
def cached_icon_for_file(f, dirs_only):
	if dirs_only or f.endswith(slash):
		norm = slash
	else:
		dot = f.rfind(".")
		if dot != -1:
			norm = f[dot:]
		else:
			norm = f[f.rfind(slash):]
	

	if norm not in icon_cache:
		icon_cache[norm] = load_icon_for_file(f)
	
	return icon_cache[norm]


def load_icon_for_file(f):
	icon_name, flags = gnome.ui.icon_lookup(ICON_THEME, factory,
				f, "",
				gnome.ui.ICON_LOOKUP_FLAGS_NONE)

	return load_icon(icon_name)
	
# We load the icon file, and if it fails load an empty one
# If the iconfile is a path starting with /, load the file
# else try to load a stock or named icon name
def load_icon(icon, width=ICON_HEIGHT, height=ICON_HEIGHT):
	pixbuf = None
	if icon != None and icon != "":
		try:
			if icon.startswith("/"):
				pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icon, width, height)
			else:
				pixbuf = ICON_THEME.load_icon(splitext(icon)[0], width, gtk.ICON_LOOKUP_USE_BUILTIN)
		except Exception, msg1:
			try:
				pixbuf = ICON_THEME.load_icon(icon, width, gtk.ICON_LOOKUP_USE_BUILTIN)
			except Exception, msg2:
				print 'Error:load_icon:Icon Load Error:%s (or %s)' % (msg1, msg2)

	# an icon that is too tall will make the EntryCompletion look funny
	if pixbuf != None and pixbuf.get_height() > height:
		pixbuf = pixbuf.scale_simple(width, height, gtk.gdk.INTERP_BILINEAR)
	return pixbuf
