#cython: boundscheck=False
#cython: cdivision=True

from SDL cimport *
from pygame cimport *
from core cimport *

from stdio cimport *
from stdlib cimport memcpy

from pygame import mixer
from retro_globals import HACK_need_audio_sample

cdef Mix_Chunk* sdl_mixchunk = NULL
cdef object pycb_audbatch = lambda sound: None

cdef int16_t soundbufs[2][512*2] # double buffered
cdef int currentbuf = 0
cdef int writepos = 0

cdef inline int int_min(int a, int b) nogil: return a if a <= b else b

cpdef pygame_mixer_init(EmulatedSystem core):
	mixer.init(
		frequency = int(core.av_info.timing.sample_rate) or 32000,
		size=-16, channels=2, buffer=512
	)

cdef size_t sdl_audio_sample_batch(int16_t* data, size_t frames) nogil:
	global sdl_mixchunk, soundbufs, currentbuf, writepos

	cdef size_t writeamount = frames*2*sizeof(int16_t)

	memcpy(
		<Uint8*>soundbufs[currentbuf] + writepos,
		<Uint8*>data,
		int_min(writeamount, sizeof(soundbufs[0]) - writepos)
	)
	writepos += writeamount
	if writepos >= sizeof(soundbufs[0]):
		if sdl_mixchunk:
			Mix_FreeChunk(sdl_mixchunk)
		sdl_mixchunk = Mix_QuickLoad_RAW(<Uint8*>soundbufs[currentbuf], sizeof(soundbufs[0]))
		Mix_PlayChannel(-1, sdl_mixchunk, 0)

		writepos %= sizeof(soundbufs[0])
		currentbuf = 1-currentbuf
		memcpy(
			<Uint8*>soundbufs[currentbuf],
			<Uint8*>data + (writeamount - writepos),
			writepos
		)

	return frames

cdef void sdl_audio_sample(int16_t left, int16_t right) nogil:
	cdef int16_t data[2]
	data[0] = left
	data[1] = right
	sdl_audio_sample_batch(<int16_t*>data, 1)



cpdef set_audio_sample_internal(EmulatedSystem core):
	""" Sets up an internal callback to play sound with SDL_mixer. """
	if not mixer.get_init():
		pygame_mixer_init(core)
	if core.name in HACK_need_audio_sample:
		print core.name, 'cannot use audio_sample_batch, wrapping it with audio_sample...'
		core.llw.set_audio_sample(sdl_audio_sample)
	else:
		core.llw.set_audio_sample_batch(sdl_audio_sample_batch)


# broken:

cdef size_t sdl_audio_sample_batch_with_pycb(int16_t* data, size_t frames):
	global pycb_audbatch
	global sdl_mixchunk, soundbufs, currentbuf, writepos

	cdef size_t writeamount = frames*2*sizeof(int16_t)

	memcpy(
		<Uint8*>soundbufs[currentbuf] + writepos,
		<Uint8*>data,
		int_min(writeamount, sizeof(soundbufs[0]) - writepos)
	)
	writepos += writeamount
	if writepos >= sizeof(soundbufs[0]):
		if sdl_mixchunk:
			Mix_FreeChunk(sdl_mixchunk)
		sdl_mixchunk = Mix_QuickLoad_RAW(<Uint8*>soundbufs[currentbuf], sizeof(soundbufs[0]))

		pg_sound = PySound_New(sdl_mixchunk)
		print pg_sound
		pycb_audbatch(pg_sound)

		writepos -= sizeof(soundbufs[0])
		currentbuf = 1-currentbuf
		memcpy(
			<Uint8*>soundbufs[currentbuf],
			<Uint8*>data + (writeamount - writepos),
			writepos
		)

	return frames

cpdef set_audio_sample_cb(EmulatedSystem core, callback=mixer.Sound.play):
	""" Sets the callback that will handle updated audio samples.
	Unlike core.EmulatedSNES.set_audio_sample_cb, the callback passed to this
	function should accept only one parameter:
		"snd" is a pygame.mixer.Sound containing the last 512 samples.
	If no callback function is provided, the default implementation of
	snd.play() is used.
	WARNING: this is currently bugged, as the function to create a new
	pygame Sound object from an SDL_mixer Mix_Chunk causes a crash.
	"""
	global pycb_audbatch
	pycb_audbatch = callback
	if not mixer.get_init():
		pygame_mixer_init(core)
	core.llw.set_audio_sample_batch(sdl_audio_sample_batch_with_pycb)

