import ctypes

# callback types

retro_environment_t = ctypes.CFUNCTYPE(ctypes.c_bool,	
                                       ctypes.c_uint,   # cmd
									   ctypes.c_void_p) # data
retro_video_refresh_t = ctypes.CFUNCTYPE(None,
                                         ctypes.c_void_p, # data
										 ctypes.c_uint,   # width
										 ctypes.c_uint,   # height
										 ctypes.c_size_t) # pitch
retro_audio_sample_t = ctypes.CFUNCTYPE(None,
                                        ctypes.c_int16, # left
										ctypes.c_int16) # right
retro_audio_sample_batch_t = ctypes.CFUNCTYPE(ctypes.c_size_t,
                                              ctypes.POINTER(ctypes.c_int16), # data
											  ctypes.c_size_t)                # frames
retro_input_poll_t = ctypes.CFUNCTYPE(None)
retro_input_state_t = ctypes.CFUNCTYPE(ctypes.c_int16,
									   ctypes.c_uint, # port	
									   ctypes.c_uint, # device
									   ctypes.c_uint, # index
									   ctypes.c_uint) # id

# structures

class retro_message(ctypes.Structure):
	_fields_ = [
		("msg",    ctypes.c_char_p),
		("frames", ctypes.c_uint),
	]

class retro_system_info(ctypes.Structure):
	_fields_ = [
		("library_name",     ctypes.c_char_p),
		("library_version",  ctypes.c_char_p),
		("valid_extensions", ctypes.c_char_p),
		("need_fullpath",    ctypes.c_bool),
		("block_extract",    ctypes.c_bool),
	]

class retro_game_geometry(ctypes.Structure):
	_fields_ = [
		("base_width",   ctypes.c_uint),
		("base_height",  ctypes.c_uint),
		("max_width",    ctypes.c_uint),
		("max_height",   ctypes.c_uint),
		("aspect_ratio", ctypes.c_float),
	]

class retro_system_timing(ctypes.Structure):
	_fields_ = [
		("fps",         ctypes.c_double),
		("sample_rate", ctypes.c_double),
	]

class retro_system_av_info(ctypes.Structure):
	_fields_ = [
		("geometry", retro_game_geometry),
		("timing",   retro_system_timing),
	]

class retro_variable(ctypes.Structure):
	_fields_ = [
		("key",   ctypes.c_char_p),
		("value", ctypes.c_char_p),
	]

class retro_game_info(ctypes.Structure):
	_fields_ = [
		("path", ctypes.c_char_p),
		("data", ctypes.c_void_p),
		("size", ctypes.c_size_t),
		("meta", ctypes.c_char_p),
	]

