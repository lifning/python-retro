"""
Pygame output for libretro Video.
"""
import pygame, ctypes

def set_video_refresh_cb(core, callback):
	"""
	Sets the callback that will handle updated video frames.

	Unlike core.EmulatedSystem.set_video_refresh_cb, the callback passed to this
	function should accept only one parameter:

		"surf" is an instance of pygame.Surface containing the frame data.
	"""

	bpp = 15
	bitmasks = (0x7c00, 0x03e0, 0x001f, 0)
	# TODO: use 24 bit if appropriate environment has been set
	if False:
		bpp = 24
		bitmasks = (0xFF0000, 0x00FF00, 0x0000FF, 0)

	def wrapper(data, width, height, pitch):
		# FIXME: "pitch//2" assumes 15-bit
		convsurf = pygame.Surface( (pitch//2, height), depth=bpp, masks=bitmasks )
		surf = convsurf.subsurface((0,0,width,height))

		# this try-except block works around a bug in pygame 1.9.1 on 64-bit hosts.
		# http://archives.seul.org/pygame/users/Apr-2011/msg00069.html
		# https://bitbucket.org/pygame/pygame/issue/109/bufferproxy-indexerror-exception-thrown
		try:
			convsurf.get_buffer().write(ctypes.string_at(data, pitch*height), 0)
		except IndexError:
			return

		callback(surf)

	core.set_video_refresh_cb(wrapper)

def set_video_refresh_surface(core, targetsurf):
	def wrapper(surf):
		targetsurf.blit(surf, (0,0))
	set_video_refresh_cb(core, wrapper)

def pygame_display_set_mode(core, use_max=True):
	key = 'max_size' if use_max else 'base_size'
	return pygame.display.set_mode(core.get_av_info()[key])

