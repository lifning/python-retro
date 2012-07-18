#cython: boundscheck=False
#cython: cdivision=True

cdef extern from 'dlfcn.h':
	void *dlopen(char *filename, int flag)
	char *dlerror()
	void *dlsym(void *handle, char *symbol)
	int dlclose(void *handle)

	unsigned RTLD_LAZY
	unsigned RTLD_NOW
	unsigned RTLD_NOLOAD
	unsigned RTLD_DEEPBIND
	unsigned RTLD_GLOBAL
	unsigned RTLD_NODELETE

cdef extern from 'stdio.h':
	int puts(char* s) nogil
	int printf(char *format, ...) nogil
	int snprintf(char *str, size_t size, char *format, ...) nogil

cdef extern from 'stdlib.h':
	void free(void* ptr) nogil
	void* malloc(size_t size) nogil
	void* realloc(void* ptr, size_t size) nogil

cdef extern from 'string.h':
	void *memcpy(void *dest, void *src, size_t n) nogil

cdef bool debug = True

cdef void null_video_refresh(void* data, unsigned width, unsigned height, size_t pitch) nogil:
	global debug
	if debug: puts('video_refresh')

cdef void null_audio_sample(int16_t left, int16_t right) nogil:
	global debug
	if debug: puts('audio_sample')

cdef size_t null_audio_sample_batch(int16_t* data, size_t frames) nogil:
	global debug
	if debug: puts('audio_sample_batch')
	return frames

cdef void null_input_poll() nogil:
	global debug
	if debug: puts('input_poll')

cdef int16_t null_input_state(unsigned port, unsigned device, unsigned index, unsigned id) nogil:
	global debug
	if debug: puts('input_state')
	return 0

cdef bool null_environment(unsigned cmd, void* data) nogil:
	global debug
	if debug: puts('environment')
	return False

cdef class LowLevelWrapper:
	def __cinit__(self, char *libpath):
		self.handle = dlopen(libpath, RTLD_LAZY)
		self.error = dlerror()
		if self.error or not self.handle:  return

		self.set_environment = <set_environment_t> dlsym(self.handle, 'retro_set_environment')
		self.set_video_refresh = <set_video_refresh_t> dlsym(self.handle, 'retro_set_video_refresh')
		self.set_audio_sample = <set_audio_sample_t> dlsym(self.handle, 'retro_set_audio_sample')
		self.set_audio_sample_batch = <set_audio_sample_batch_t> dlsym(self.handle, 'retro_set_audio_sample_batch')
		self.set_input_poll = <set_input_poll_t> dlsym(self.handle, 'retro_set_input_poll')
		self.set_input_state = <set_input_state_t> dlsym(self.handle, 'retro_set_input_state')
		self.init = <init_t> dlsym(self.handle, 'retro_init')
		self.deinit = <deinit_t> dlsym(self.handle, 'retro_deinit')
		self.api_version = <api_version_t> dlsym(self.handle, 'retro_api_version')
		self.get_system_info = <get_system_info_t> dlsym(self.handle, 'retro_get_system_info')
		self.get_system_av_info = <get_system_av_info_t> dlsym(self.handle, 'retro_get_system_av_info')
		self.set_controller_port_device = <set_controller_port_device_t> dlsym(self.handle, 'retro_set_controller_port_device')
		self.reset = <reset_t> dlsym(self.handle, 'retro_reset')
		self.run = <run_t> dlsym(self.handle, 'retro_run')
		self.serialize_size = <serialize_size_t> dlsym(self.handle, 'retro_serialize_size')
		self.serialize = <serialize_t> dlsym(self.handle, 'retro_serialize')
		self.unserialize = <unserialize_t> dlsym(self.handle, 'retro_unserialize')
		self.cheat_reset = <cheat_reset_t> dlsym(self.handle, 'retro_cheat_reset')
		self.cheat_set = <cheat_set_t> dlsym(self.handle, 'retro_cheat_set')
		self.load_game = <load_game_t> dlsym(self.handle, 'retro_load_game')
		self.load_game_special = <load_game_special_t> dlsym(self.handle, 'retro_load_game_special')
		self.unload_game = <unload_game_t> dlsym(self.handle, 'retro_unload_game')
		self.get_region = <get_region_t> dlsym(self.handle, 'retro_get_region')
		self.get_memory_data = <get_memory_data_t> dlsym(self.handle, 'retro_get_memory_data')
		self.get_memory_size = <get_memory_size_t> dlsym(self.handle, 'retro_get_memory_size')

		self.error = dlerror()
		if not self.error:
			self.init()
			self.set_null_callbacks() # TODO: not assume this?
			# is it okay to assign an audio_sample_batch and replace it with an
			# audio_sample afterward?

	def __dealloc__(self):
		dlclose(self.handle)

	cdef public void set_null_callbacks(self):
		global debug
		self.set_video_refresh(null_video_refresh)
		## this would be less performant i think, due to more function calls:
		#self.set_audio_sample(null_audio_sample)
		self.set_audio_sample_batch(null_audio_sample_batch)
		self.set_input_poll(null_input_poll)
		self.set_input_state(null_input_state)


cdef class EmulatedSystem:
	def __cinit__(self, char* libpath):
		# todo: move libpath to a temp file and load that, for multithread
		self.llw = LowLevelWrapper(libpath)
		if not self.llw.error:
			self.llw.init()

	def __init__(self, char* libpath):
		self._loaded_cheats = {} 

	def __dealloc__(self):
		if self.llw and not self.llw.error:
			self.llw.deinit()
			#del self.llw

	def _reload_cheats(self):
		""" Internal method.
		Reloads cheats in the emulated console from the _loaded_cheats variable.
		"""
		self.llw.cheat_reset()
		for index, (code, enabled) in self._loaded_cheats.items():
			self.llw.cheat_set(index, enabled, code)

	def _memory_to_string(self, unsigned mem_type):
		""" Internal method.
		Copies data from the given libretro memory buffer into a new string.
		"""
		cdef size_t mem_size = self.llw.get_memory_size(mem_type)
		cdef char* mem_data = <char*> self.llw.get_memory_data(mem_type)

		return <bytes>(mem_data[:mem_size])

	def _string_to_memory(self, bytes data, unsigned mem_type):
		""" Internal method.
		Copies the given data into the libretro memory buffer of the given type.
		"""
		cdef size_t mem_size = self.llw.get_memory_size(mem_type)
		cdef char* mem_data = <char*> self.llw.get_memory_data(mem_type)

		if len(data) != mem_size:
			raise Exception(
				"This game requires {} bytes of memory type {}, not {} bytes".format(
					mem_size, mem_type, len(data)
				)
			)
		memcpy(mem_data, <char*>data, mem_size)

	cpdef _require_game_loaded(self):
		""" Raise an exception if a game is not loaded. """
		if not self._game_loaded:
			raise Exception("This method requires that a game be loaded!")

	cpdef _require_game_not_loaded(self):
		""" Raise an exception if a game is already loaded. """
		if self._game_loaded:
			raise Exception("This method requires that no game be loaded!")

	cpdef set_controller_port_device(self, unsigned port, unsigned device):
		""" Connects the given device to the given controller port.

		Connecting a device to a port implicitly removes any device previously
		connected to that port. To remove a device without connecting a new
		one, pass DEVICE_NONE as the device parameter. From this point onward,
		the callback passed to set_input_state_cb() will be called with the
		appropriate device, index and id parameters.

		Whenever you call a load_game_* function a DEVICE_JOYPAD will be
		connected to both ports, and devices previously connected using this
		function will be disconnected.
		"""
		self.llw.set_controller_port_device(port, device)

	cpdef reset(self):
		""" Press the reset button on the emulated console.
		Requires that a game be loaded.
		"""
		self._require_game_loaded()
		self.llw.reset()

	cpdef run(self, int frames=1):
		""" Run the emulated console for a given number of frames (default 1).
		Before this function returns, the registered callbacks will be called
		at least once each.
		Requires that a game be loaded.
		WARNING: for performance reasons, an exception isn't raised.
		"""
		if self._game_loaded:
			while frames > 0:
				frames -= 1
				self.llw.run()

	cpdef unload(self):
		""" Remove the game and return its non-volatile storage contents.

		Returns a list with an entry for each MEMORY_* constant in
		VALID_MEMORY_TYPES. If the current game uses that type of storage,
		the corresponding index in the list will be a string containing the
		storage contents, which can later be passed to load_game_*.
		Otherwise, the corresponding index is None.

		Requires that a game be loaded.
		"""
		VALID_MEMORY_TYPES = [ RETRO_MEMORY_SAVE_RAM, RETRO_MEMORY_RTC ]

		self._require_game_loaded()

		res = [self._memory_to_string(t) for t in VALID_MEMORY_TYPES]
		self.llw.unload_game()
		self._loaded_cheats = {}
		self._game_loaded = False
		return res

	cpdef get_refresh_rate(self):
		""" Return the intended refresh-rate of the loaded game. """
		self._require_game_loaded()
		return float(self.av_info.timing.fps)

	cpdef serialize(self):
		""" Serializes the state of the emulated console to a string.
		Requires that a game be loaded.
		"""
		cdef size_t size = self.llw.serialize_size()
		cdef char* buf = <char*> malloc(size)
		cdef bool res = self.llw.serialize(buf, size)
		if not res:
			raise Exception("problem in serialize")
		try:
			return <bytes>(buf[:size])
		finally:
			free(buf)

	cpdef unserialize(self, bytes state):
		""" Restores the state of the emulated console from a string.
		Note that the game's SRAM data is part of the saved state.
		Requires that the same game that was loaded when serialize was
		called, be loaded before unserialize is called.
		"""
		cdef bool res = self.llw.unserialize(<char*>state, len(state))
		if not res:
			raise Exception("problem in unserialize")

	def cheat_add(self, index, code, enabled=True):
		""" Stores the given cheat code at the given index in the cheat list.
		"index" must be an integer. Only one cheat can be stored per index.
		"code" must be a string containing one or more codes delimited by '+'.
		"enabled" must be a boolean describing whether the cheat code is active.
		"""
		self._loaded_cheats[index] = (code, enabled)
		self._reload_cheats()

	def cheat_remove(self, index):
		""" Removes the cheat at the given index from the cheat list.
		"index" must be an integer previously passed to cheat_add.
		"""
		del self._loaded_cheats[index]
		self._reload_cheats()

	def cheat_set_enabled(self, index, enabled):
		""" Enables or disables the cheat at the given index in the cheat list.
		"index" must be an integer previously passed to cheat_add.
		"enabled" must be a boolean describing whether the cheat code is active.
		"""
		code, _ = self._loaded_cheats[index]
		self._loaded_cheats[index] = (code, enabled)
		self._reload_cheats()

	def cheat_is_enabled(self, index):
		""" Returns true if the cheat at the given index is enabled.
		"index" must be an integer previously passed to cheat_add.
		"""
		_, enabled = self._loaded_cheats[index]
		return enabled

	def load_game_normal(self, data=None, sram=None, rtc=None, path=None, get_data_from_path=True):
		""" Load an ordinary game into the emulated console.
		"data" should be a string containing the raw game image.
			If None, you must provide 'path'.
		"sram" should be a string containing the persistent SRAM data.
			If None, the game will be given an empty SRAM to start.
		"rtc" should be a string containing the real-time-clock data.
			If None, the game will be given a fresh, blank RTC region.
		"path" should be a string containing the file path to the game.
			If None, you must provide 'data'.
		"get_data_from_path" will read the file into 'data' if 'data' is None.
		"""
		cdef retro_game_info gameinfo
		cdef retro_system_info sysinfo
		self._require_game_not_loaded()

		gameinfo.path = NULL
		gameinfo.data = NULL
		gameinfo.size = 0
		gameinfo.meta = NULL

		self.llw.get_system_info(&sysinfo)

		if path:
			gameinfo.path = <char*>path
			if get_data_from_path and not data:
				data = open(path, 'rb').read()
		elif sysinfo.need_fullpath:
			raise Exception('The loaded libretro needs a full path to the ROM')

		if data:
			gameinfo.data = <char*>data
			gameinfo.size = len(data)
		elif not path:
			raise Exception('Must provide either file path or raw loaded game!')

		self.llw.load_game(&gameinfo)
		self.llw.get_system_av_info(&(self.av_info))
		self._game_loaded = True

		if sram: self._string_to_memory(sram, RETRO_MEMORY_SAVE_RAM)
		if rtc:  self._string_to_memory(rtc, RETRO_MEMORY_RTC)

	cpdef get_library_info(self):
		cdef retro_system_info info
		self.llw.get_system_info(&info)
		return {
			'api':  int(self.llw.api_version()),
			'name': str(info.library_name),
			'ver':  str(info.library_version),
			'exts': str(info.valid_extensions),
		}

	cpdef get_av_info(self):
		self._require_game_loaded()
		return {
			'base_size': (
				int(self.av_info.geometry.base_width), int(self.av_info.geometry.base_height)
			),
			'max_size': (
				int(self.av_info.geometry.max_width), int(self.av_info.geometry.max_height)
			),
			'aspect_ratio': float(self.av_info.geometry.aspect_ratio),
			'fps':          float(self.av_info.timing.fps),
			'sample_rate':  float(self.av_info.timing.sample_rate),
		}

	cpdef close(self):
		""" Release all resources associated with this library instance. """
		self.llw.deinit()
		self.llw.set_null_callbacks()



# backwards-compat with old python-snes api...
cdef class EmulatedSNES(EmulatedSystem):
	def load_cartridge_normal(self, *args):
		return self.load_game_normal(*args)

	def _require_cart_loaded(self):
		return self._require_game_loaded()

	def _require_cart_not_loaded(self):
		return self._require_game_not_loaded()

