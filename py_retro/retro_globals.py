import ctypes


# constants

DEVICE_MASK = 0xff

DEVICE_NONE     = 0
DEVICE_JOYPAD   = 1
DEVICE_MOUSE    = 2
DEVICE_KEYBOARD = 3
DEVICE_LIGHTGUN = 4
DEVICE_ANALOG   = 5

DEVICE_JOYPAD_MULTITAP      = ((1 << 8) | DEVICE_JOYPAD)
DEVICE_LIGHTGUN_SUPER_SCOPE = ((1 << 8) | DEVICE_LIGHTGUN)
DEVICE_LIGHTGUN_JUSTIFIER   = ((2 << 8) | DEVICE_LIGHTGUN)
DEVICE_LIGHTGUN_JUSTIFIERS  = ((3 << 8) | DEVICE_LIGHTGUN)

DEVICE_ID_JOYPAD_B      =  0
DEVICE_ID_JOYPAD_Y      =  1
DEVICE_ID_JOYPAD_SELECT =  2
DEVICE_ID_JOYPAD_START  =  3
DEVICE_ID_JOYPAD_UP     =  4
DEVICE_ID_JOYPAD_DOWN   =  5
DEVICE_ID_JOYPAD_LEFT   =  6
DEVICE_ID_JOYPAD_RIGHT  =  7
DEVICE_ID_JOYPAD_A      =  8
DEVICE_ID_JOYPAD_X      =  9
DEVICE_ID_JOYPAD_L      = 10
DEVICE_ID_JOYPAD_R      = 11
DEVICE_ID_JOYPAD_L2     = 12
DEVICE_ID_JOYPAD_R2     = 13
DEVICE_ID_JOYPAD_L3     = 14
DEVICE_ID_JOYPAD_R3     = 15


DEVICE_INDEX_ANALOG_LEFT  = 0
DEVICE_INDEX_ANALOG_RIGHT = 1
DEVICE_ID_ANALOG_X        = 0
DEVICE_ID_ANALOG_Y        = 1

DEVICE_ID_MOUSE_X     = 0
DEVICE_ID_MOUSE_Y     = 1
DEVICE_ID_MOUSE_LEFT  = 2
DEVICE_ID_MOUSE_RIGHT = 3

DEVICE_ID_LIGHTGUN_X       = 0
DEVICE_ID_LIGHTGUN_Y       = 1
DEVICE_ID_LIGHTGUN_TRIGGER = 2
DEVICE_ID_LIGHTGUN_CURSOR  = 3
DEVICE_ID_LIGHTGUN_TURBO   = 4
DEVICE_ID_LIGHTGUN_PAUSE   = 5
DEVICE_ID_LIGHTGUN_START   = 6

REGION_NTSC = 0
REGION_PAL  = 1

MEMORY_MASK       = 0xff
MEMORY_SAVE_RAM   = 0
MEMORY_RTC        = 1
MEMORY_SYSTEM_RAM = 2
MEMORY_VIDEO_RAM  = 3

MEMORY_SNES_BSX_RAM            = ((1 << 8) | MEMORY_SAVE_RAM)
MEMORY_SNES_BSX_PRAM           = ((2 << 8) | MEMORY_SAVE_RAM)
MEMORY_SNES_SUFAMI_TURBO_A_RAM = ((3 << 8) | MEMORY_SAVE_RAM)
MEMORY_SNES_SUFAMI_TURBO_B_RAM = ((4 << 8) | MEMORY_SAVE_RAM)
MEMORY_SNES_GAME_BOY_RAM       = ((5 << 8) | MEMORY_SAVE_RAM)
MEMORY_SNES_GAME_BOY_RTC       = ((6 << 8) | MEMORY_RTC)

GAME_TYPE_BSX            = 0x101
GAME_TYPE_BSX_SLOTTED    = 0x102
GAME_TYPE_SUFAMI_TURBO   = 0x103
GAME_TYPE_SUPER_GAME_BOY = 0x104

ENVIRONMENT_SET_ROTATION          =  1
ENVIRONMENT_GET_OVERSCAN          =  2
ENVIRONMENT_GET_CAN_DUPE          =  3
ENVIRONMENT_GET_VARIABLE          =  4
ENVIRONMENT_SET_VARIABLES         =  5
ENVIRONMENT_SET_MESSAGE           =  6
ENVIRONMENT_SHUTDOWN              =  7
ENVIRONMENT_SET_PERFORMANCE_LEVEL =  8
ENVIRONMENT_GET_SYSTEM_DIRECTORY  =  9
ENVIRONMENT_SET_PIXEL_FORMAT      = 10

PIXEL_FORMAT_0RGB1555 = 0
PIXEL_FORMAT_XRGB8888 = 1


# types

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

