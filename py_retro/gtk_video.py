"""
PyGTK drawable output for libretro Video.
"""
import pygtk
pygtk.require("2.0")
import gtk, gobject, ctypes

def _decode_pixel(pixel):
	"""Decode a SNES pixel into an (r,g,b) tuple."""
	r = (pixel & 0b0111110000000000) >> 7
	g = (pixel & 0b0000001111100000) >> 2
	b = (pixel & 0b0000000000011111) << 3

	return "%c%c%c" % (
		(r | (r >> 5)),
		(g | (g >> 5)),
		(b | (b >> 5)),
	)

_rgb_lookup = [_decode_pixel(_p) for _p in xrange(32768)]
def xrgb1555_to_rgb888(data, width, height, pitch):
	return ''.join(
		_rgb_lookup[data[(pitch//2)*y + x]]
		for y in xrange(height)
		for x in xrange(width)
	)

def set_video_refresh_drawable(core, canvas):
	"""
	Sets the gtk.DrawingArea that will receive updated video frames.
	"""
	# TODO: skip conversion from 16 to 24 if appropriate environment is set
	def wrapper(data, width, height, pitch):
		raw = ctypes.cast(data, ctypes.POINTER(ctypes.c_uint16))
		canvas.window.draw_rgb_image(
			canvas.get_style().fg_gc[gtk.STATE_NORMAL],
			0,0, width,height,
			gtk.gdk.RGB_DITHER_NONE,
			xrgb1555_to_rgb888(raw, width, height, pitch),
			-1
		)

	core.set_video_refresh_cb(wrapper)

def gtk_DrawingArea(core, use_max=True):
	"""
	Gets a new gtk.DrawingArea that will receive updated video frames.
	"""
	key = 'max_size' if use_max else 'base_size'
	w,h = core.get_av_info()[key]
	canvas = gtk.DrawingArea()
	canvas.set_size_request(w, h)
	canvas.show()
	set_video_refresh_drawable(core, canvas)
	return canvas


