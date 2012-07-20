import ctypes

from retro_globals import *

debug = False

def null_video_refresh(data, width, height, pitch):
	global debug
	if debug: print('video_refresh')

def null_audio_sample(left, right):
	global debug
	if debug: print('audio_sample')

def null_audio_sample_batch(data, frames):
	global debug
	if debug: print('audio_sample_batch')
	return frames

def null_input_poll():
	global debug
	if debug: print('input_poll')

def null_input_state(port, device, index, id):
	global debug
	if debug: print('input_state')
	return 0

def null_environment(cmd, data):
	global debug
	if debug: print('environment')
	return False

class LowLevelWrapper(ctypes.CDLL):
	def __init__(self, libpath):
		ctypes.CDLL.__init__(self, libpath)

		self.retro_set_environment.restype = None
		self.retro_set_environment.argtypes = [retro_environment_t]

		self.retro_set_video_refresh.restype = None
		self.retro_set_video_refresh.argtypes = [retro_video_refresh_t]

		self.retro_set_audio_sample.restype = None
		self.retro_set_audio_sample.argtypes = [retro_audio_sample_t]

		self.retro_set_audio_sample_batch.restype = None
		self.retro_set_audio_sample_batch.argtypes = [retro_audio_sample_batch_t]

		self.retro_set_input_poll.restype = None
		self.retro_set_input_poll.argtypes = [retro_input_poll_t]

		self.retro_set_input_state.restype = None
		self.retro_set_input_state.argtypes = [retro_input_state_t]

		self.retro_init.restype = None
		self.retro_init.argtypes = []

		self.retro_deinit.restype = None
		self.retro_deinit.argtypes = []

		self.retro_api_version.restype = ctypes.c_uint
		self.retro_api_version.argtypes = []

		self.retro_get_system_info.restype = None
		self.retro_get_system_info.argtypes = [ctypes.POINTER(retro_system_info)]

		self.retro_get_system_av_info.restype = None
		self.retro_get_system_av_info.argtypes = [ctypes.POINTER(retro_system_av_info)]

		self.retro_set_controller_port_device.restype = None
		self.retro_set_controller_port_device.argtypes = [ctypes.c_uint, ctypes.c_uint]

		self.retro_reset.restype = None
		self.retro_reset.argtypes = []

		self.retro_run.restype = None
		self.retro_run.argtypes = []

		self.retro_serialize_size.restype = ctypes.c_size_t
		self.retro_serialize_size.argtypes = []

		self.retro_serialize.restype = ctypes.c_bool
		self.retro_serialize.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

		self.retro_unserialize.restype = ctypes.c_bool
		self.retro_unserialize.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

		self.retro_cheat_reset.restype = None
		self.retro_cheat_reset.argtypes = []

		self.retro_cheat_set.restype = None
		self.retro_cheat_set.argtypes = [ ctypes.c_uint, ctypes.c_bool, ctypes.c_char_p ]

		self.retro_load_game.restype = ctypes.c_bool
		self.retro_load_game.argtypes = [ctypes.POINTER(retro_game_info)]

		self.retro_load_game_special.restype = ctypes.c_bool
		self.retro_load_game_special.argtypes = [ctypes.c_uint, ctypes.POINTER(retro_game_info), ctypes.c_size_t]

		self.retro_unload_game.restype = None
		self.retro_unload_game.argtypes = []

		self.retro_get_region.restype = ctypes.c_uint
		self.retro_get_region.argtypes = []

		self.retro_get_memory_data.restype = ctypes.c_void_p
		self.retro_get_memory_data.argtypes = [ctypes.c_uint]

		self.retro_get_memory_size.restype = ctypes.c_size_t
		self.retro_get_memory_size.argtypes = [ctypes.c_uint]

		# set "retro_"-less aliases for brevity
		self.set_environment = self.retro_set_environment
		self.set_video_refresh = self.retro_set_video_refresh
		self.set_audio_sample = self.retro_set_audio_sample
		self.set_audio_sample_batch = self.retro_set_audio_sample_batch
		self.set_input_poll = self.retro_set_input_poll
		self.set_input_state = self.retro_set_input_state
		self.init = self.retro_init
		self.deinit = self.retro_deinit
		self.api_version = self.retro_api_version
		self.get_system_info = self.retro_get_system_info
		self.get_system_av_info = self.retro_get_system_av_info
		self.set_controller_port_device = self.retro_set_controller_port_device
		self.reset = self.retro_reset
		self.run = self.retro_run
		self.serialize_size = self.retro_serialize_size
		self.serialize = self.retro_serialize
		self.unserialize = self.retro_unserialize
		self.cheat_reset = self.retro_cheat_reset
		self.cheat_set = self.retro_cheat_set
		self.load_game = self.retro_load_game
		self.load_game_special = self.retro_load_game_special
		self.unload_game = self.retro_unload_game
		self.get_region = self.retro_get_region
		self.get_memory_data = self.retro_get_memory_data
		self.get_memory_size = self.retro_get_memory_size


class EmulatedSystem:
	_video_refresh_wrapper = None
	_audio_sample_wrapper = None
	_audio_sample_batch_wrapper = None
	_input_poll_wrapper = None
	_input_state_wrapper = None
	_environment_wrapper = None

	def __init__(self, libpath):
		# todo: move libpath to a temp file and load that, for multithread
		self.llw = LowLevelWrapper(libpath)
		self.llw.init() # initialize libretro
		self._reset_vars()
		self.set_null_callbacks() # TODO: not assume this?
		# is it okay to assign an audio_sample_batch and replace it with an
		# audio_sample afterward?

	def _reset_vars(self):
		self._loaded_cheats = {}
		self._game_loaded = False
		self.av_info = retro_system_av_info()

	def __del__(self):
		self.llw.deinit()

	def _reload_cheats(self):
		""" Internal method.
		Reloads cheats in the emulated console from the _loaded_cheats variable.
		"""
		self.llw.cheat_reset()
		for index, (code, enabled) in self._loaded_cheats.items():
			self.llw.cheat_set(index, enabled, code)

	def _memory_to_string(self, mem_type):
		""" Internal method.
		Copies data from the given libretro memory buffer into a new string.
		"""
		mem_size = self.llw.get_memory_size(mem_type)
		mem_data = self.llw.get_memory_data(mem_type)

		if mem_size == 0:
			return None

		buf = ctypes.create_string_buffer(mem_size)
		ctypes.memmove(buf, mem_data, mem_size)

		return buf.raw

	def _string_to_memory(self, data, mem_type):
		""" Internal method.
		Copies the given data into the libretro memory buffer of the given type.
		"""
		mem_size = self.llw.get_memory_size(mem_type)
		mem_data = self.llw.get_memory_data(mem_type)

		if len(data) != mem_size:
			raise Exception(
				"This game requires {} bytes of memory type {}, not {} bytes".format(
					mem_size, mem_type, len(data)
				)
			)
		ctypes.memmove(mem_data, data, mem_size)

	def _require_game_loaded(self):
		""" Raise an exception if a game is not loaded. """
		if not self._game_loaded:
			raise Exception("This method requires that a game be loaded!")

	def _require_game_not_loaded(self):
		""" Raise an exception if a game is already loaded. """
		if self._game_loaded:
			raise Exception("This method requires that no game be loaded!")

	def set_controller_port_device(self, port, device):
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

	def reset(self):
		""" Press the reset button on the emulated console.
		Requires that a game be loaded.
		"""
		self._require_game_loaded()
		self.llw.reset()

	def run(self, frames=1):
		""" Run the emulated console for a given number of frames (default 1).
		Before this function returns, the registered callbacks will be called
		at least once each.
		Requires that a game be loaded.
		WARNING: for performance reasons, an exception isn't raised.
		"""
		self._require_game_loaded()
		while frames > 0:
			frames -= 1
			self.llw.run()

	def unload(self):
		""" Remove the game and return its non-volatile storage contents.

		Returns a list with an entry for each MEMORY_* constant in
		VALID_MEMORY_TYPES. If the current game uses that type of storage,
		the corresponding index in the list will be a string containing the
		storage contents, which can later be passed to load_game_*.
		Otherwise, the corresponding index is None.

		Requires that a game be loaded.
		"""
		VALID_MEMORY_TYPES = [ MEMORY_SAVE_RAM, MEMORY_RTC ]

		self._require_game_loaded()

		res = [self._memory_to_string(t) for t in VALID_MEMORY_TYPES]

		self.llw.unload_game()
		self.reset_vars()

		return res

	def get_refresh_rate(self):
		""" Return the intended refresh-rate of the loaded game. """
		self._require_game_loaded()
		return float(self.av_info.timing.fps)

	def serialize(self):
		""" Serializes the state of the emulated console to a string.
		Requires that a game be loaded.
		"""
		size = self.llw.serialize_size()
		buf = ctypes.create_string_buffer(size)
		res = self.llw.serialize(ctypes.cast(buf, ctypes.c_void_p), size)
		if not res:
			raise Exception("problem in serialize")
		return buf.raw

	def unserialize(self, state):
		""" Restores the state of the emulated console from a string.
		Note that the game's SRAM data is part of the saved state.
		Requires that the same game that was loaded when serialize was
		called, be loaded before unserialize is called.
		"""
		res = self.llw.unserialize(ctypes.cast(state, ctypes.c_void_p), len(state))
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
		self._require_game_not_loaded()

		gameinfo = retro_game_info()
		sysinfo = retro_system_info()

		self.llw.get_system_info(ctypes.byref(sysinfo))

		if path:
			gameinfo.path = ctypes.cast(path, ctypes.c_char_p)
			if get_data_from_path and not data:
				data = open(path, 'rb').read()
		elif sysinfo.need_fullpath:
			raise Exception('The loaded libretro needs a full path to the ROM')

		if data:
			gameinfo.data = ctypes.cast(data, ctypes.c_void_p)
			gameinfo.size = len(data)
		elif not path:
			raise Exception('Must provide either file path or raw loaded game!')

		self.llw.load_game(ctypes.byref(gameinfo))
		self.llw.get_system_av_info(ctypes.byref(self.av_info))
		self._game_loaded = True

		if sram: self._string_to_memory(sram, RETRO_MEMORY_SAVE_RAM)
		if rtc:  self._string_to_memory(rtc, RETRO_MEMORY_RTC)

	def get_library_info(self):
		info = retro_system_info()
		self.llw.get_system_info(ctypes.byref(info))
		return {
			'api':  int(self.llw.api_version()),
			'name': str(info.library_name),
			'ver':  str(info.library_version),
			'exts': str(info.valid_extensions),
		}

	def get_av_info(self):
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

	def close(self):
		""" Release all resources associated with this library instance. """
		self.llw.deinit()
		self._video_refresh_wrapper = None
		self._audio_sample_wrapper = None
		self._audio_sample_batch_wrapper = None
		self._input_poll_wrapper = None
		self._input_state_wrapper = None
		self._environment_wrapper = None

	def set_video_refresh_cb(self, callback):
		""" Sets the callback that will handle updated video frames.
		The callback should accept the following parameters:
			"data" is a pointer to the top-left of an array of pixels.
			"width" is the number of pixels in each row of the frame.
			"height" is the number of pixel-rows in the frame.
			"pitch" is the number of bytes between the start of each row.
		The callback should return nothing.
		"""
		self._video_refresh_wrapper = retro_video_refresh_t(callback)
		self.llw.set_video_refresh(self._video_refresh_wrapper)

	def set_audio_sample_cb(self, callback):
		""" Sets the callback that will handle updated audio frames.
		The callback should accept the following parameters:
			"left" is an int16 that specifies the left audio channel volume.
			"right" is an int16 that specifies the right audio channel volume.
		The callback should return nothing.
		"""
		self._audio_sample_wrapper = retro_audio_sample_t(callback)
		self.llw.set_audio_sample(self._audio_sample_wrapper)

	def set_audio_sample_batch_cb(self, callback):
		""" Sets the callback that will handle updated audio frames.
		The callback should accept the following parameters:
			"data" is an int16* containing stereo audio sample data
			"frames" is a size_t that specifies the number of {l,r} samples.
		The callback should return nothing.
		"""
		self._audio_sample_batch_wrapper = retro_audio_sample_batch_t(callback)
		self.llw.set_audio_sample_batch(self._audio_sample_batch_wrapper)

	def set_input_poll_cb(self, callback):
		""" Sets the callback that will check for updated input events.
		The callback should accept no parameters and return nothing.
		It should just read new input events and store them somewhere so they
		can be returned by the input state callback.
		"""
		self._input_poll_wrapper = retro_input_poll_t(callback)
		self.llw.set_input_poll(self._input_poll_wrapper)

	def set_input_state_cb(self, callback):
		""" Sets the callback that reports the current state of input devices.
		The callback should accept the following parameters:
			"port" is an int describing which controller port is being reported.
			"device" a DEVICE_* constant specifying the device type.
			"index" is a number specifying a device on a multitap.
			"id" is a DEVICE_ID_* constant specifying the button or axis.
		If "id" represents an analogue input (such as DEVICE_ID_MOUSE_X and
		DEVICE_ID_MOUSE_Y), you should return a value between -32768 and 32767.
		"""
		self._input_state_wrapper = retro_input_state_t(callback)
		self.llw.set_input_state(self._input_state_wrapper)

	def set_environment_cb(self, callback):
		self._environment_wrapper = retro_environment_t(callback)
		self.llw.set_environment(self._environment_wrapper)

	def set_null_callbacks(self):
		self.set_video_refresh_cb(null_video_refresh)
		self.set_audio_sample_batch_cb(null_audio_sample_batch)
		self.set_input_poll_cb(null_input_poll)
		self.set_input_state_cb(null_input_state)
		self.set_environment_cb(null_input_state)



# backwards-compat with old python-snes api...
class EmulatedSNES(EmulatedSystem):
	def load_cartridge_normal(self, *args):
		return self.load_game_normal(*args)

	def _require_cart_loaded(self):
		return self._require_game_loaded()

	def _require_cart_not_loaded(self):
		return self._require_game_not_loaded()

