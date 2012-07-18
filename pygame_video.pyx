from SDL cimport *
from pygame cimport *
from cy_retro cimport *

from pygame import Surface, display

cdef SDL_Surface *sdl_vidsurf = NULL
cdef SDL_Surface *sdl_bufsurf = NULL

cdef object pg_vidsurf = None
cdef object pycb_vidrefresh = lambda surf: None

cdef void sdl_video_refresh(void* data, unsigned width, unsigned height, size_t pitch) nogil:
	global sdl_vidsurf, sdl_bufsurf
	cdef int bpp = 15
	cdef unsigned rmask = 0b0111110000000000 #0x7c00
	cdef unsigned gmask = 0b0000001111100000 #0x03e0
	cdef unsigned bmask = 0b0000000000011111 #0x001f
	if sdl_vidsurf:
		if data and not sdl_bufsurf:
			# TODO: use 24 bit if appropriate environment has been set
			if False:
				bpp = 24
				rmask = 0xff0000
				gmask = 0x00ff00
				bmask = 0x0000ff
			sdl_bufsurf = SDL_CreateRGBSurfaceFrom(
				data, width, height, bpp, pitch, rmask, gmask, bmask, 0
			)
		SDL_BlitSurface(sdl_bufsurf, NULL, sdl_vidsurf, NULL)

cdef void sdl_video_refresh_with_pycb(void* data, unsigned width, unsigned height, size_t pitch):
	global pycb_vidrefresh, pg_vidsurf, sdl_vidsurf
	if not pg_vidsurf:
		pg_vidsurf = Surface((width, height))
		sdl_vidsurf = PySurface_AsSurface(pg_vidsurf)
		#sdl_vidsurf = SDL_CreateRGBSurface(0, width, height, bpp)
	sdl_video_refresh(data, width, height, pitch)
	pycb_vidrefresh(pg_vidsurf)
	#pycb_vidrefresh(PySurface_New(sdl_vidsurf))

cpdef set_video_refresh_cb(EmulatedSystem core, object callback):
	""" Sets the callback that will handle updated video frames.
		The callback passed to this function should accept only one parameter:
			"surf" is an instance of pygame.Surface containing the frame data.
	"""
	global pycb_vidrefresh, sdl_vidsurf
	pycb_vidrefresh = callback
	core.llw.set_video_refresh(sdl_video_refresh_with_pycb)

cpdef set_video_refresh_surface(EmulatedSystem core, object surf):
	""" Sets the surface that will receive frame updates. """
	global sdl_vidsurf
	sdl_vidsurf = PySurface_AsSurface(surf)
	core.llw.set_video_refresh(sdl_video_refresh)

cpdef pygame_display_set_mode(EmulatedSystem core, bool use_max=True):
	key = 'max_size' if use_max else 'base_size'
	return display.set_mode(core.get_av_info()[key])

