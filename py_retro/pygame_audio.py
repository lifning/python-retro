"""
Pygame output for SNES Audio.
"""

import pygame, numpy, ctypes

sndlog = ''

def pygame_mixer_init(core):
	pygame.mixer.init(
		frequency=int(core.get_av_info()['sample_rate'] or 32040),
		size=-16, channels=2, buffer=512
	)

def set_audio_sample_batch_cb_old(core, callback=pygame.mixer.Sound.play):
	"""
	Sets the callback that will handle updated audio samples.

	Unlike core.EmulatedSNES.set_audio_sample_cb, the callback passed to this
	function should accept only one parameter:

		"snd" is an instance of pygame.mixer.Sound containing the last 512
		samples.

	If no callback function is provided, the default implementation of
	snd.play() is used.
	"""

	sndarr = numpy.zeros((512, 2), dtype=numpy.int16, order='C')
	snd = pygame.sndarray.make_sound( sndarr )
	sndbuf = snd.get_buffer()
	maxlog = 512*2*2 # 512 stereo samples of 16-bits each

	def wrapper(data, frames):
		global sndlog

		sndlog += ctypes.string_at(data, frames*2)

		if len(sndlog) >= maxlog:
			# this try-except block works around a bug in pygame 1.9.1 on 64-bit hosts.
			# http://archives.seul.org/pygame/users/Apr-2011/msg00069.html
			# https://bitbucket.org/pygame/pygame/issue/109/bufferproxy-indexerror-exception-thrown
			try:
				sndbuf.write(sndlog[:maxlog], 0)
				callback(snd)
				sndlog = sndlog[maxlog:]
			except IndexError:
				pass

		return frames

	core.set_audio_sample_batch_cb(wrapper)

def set_audio_sample_batch_cb(core, callback=pygame.mixer.Sound.play):
	"""
	Sets the callback that will handle updated audio samples.

	Unlike core.EmulatedSNES.set_audio_sample_cb, the callback passed to this
	function should accept only one parameter:

		"snd" is an instance of pygame.mixer.Sound containing the last 512
		samples.

	If no callback function is provided, the default implementation of
	snd.play() is used.
	"""

	maxlog = 512*2*2 # 512 stereo samples of 16-bits each
	def wrapper(data, frames):
		global sndlog

		sndlog += ctypes.string_at(data, frames*2)

		if len(sndlog) >= maxlog:
			sndarr = numpy.fromstring(sndlog[:maxlog], dtype=numpy.int16).reshape((512,2))
			callback(pygame.sndarray.make_sound(sndarr))
			sndlog = sndlog[maxlog:]

		return frames

	core.set_audio_sample_batch_cb(wrapper)

def set_audio_sample_internal(core):
	set_audio_sample_batch_cb(core)

