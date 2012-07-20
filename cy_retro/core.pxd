
#from libcpp cimport bool

ctypedef int bool
ctypedef short int16_t
ctypedef unsigned char uint8_t
ctypedef unsigned short uint16_t

cdef extern from 'libretro.h':
	cdef:
		enum:
			RETRO_DEVICE_MASK = 0xff
		enum:
			RETRO_DEVICE_NONE     = 0
			RETRO_DEVICE_JOYPAD   = 1
			RETRO_DEVICE_MOUSE    = 2
			RETRO_DEVICE_KEYBOARD = 3
			RETRO_DEVICE_LIGHTGUN = 4
			RETRO_DEVICE_ANALOG   = 5
		enum:
			RETRO_DEVICE_JOYPAD_MULTITAP      = ((1 << 8) | RETRO_DEVICE_JOYPAD)
			RETRO_DEVICE_LIGHTGUN_SUPER_SCOPE = ((1 << 8) | RETRO_DEVICE_LIGHTGUN)
			RETRO_DEVICE_LIGHTGUN_JUSTIFIER   = ((2 << 8) | RETRO_DEVICE_LIGHTGUN)
			RETRO_DEVICE_LIGHTGUN_JUSTIFIERS  = ((3 << 8) | RETRO_DEVICE_LIGHTGUN)
		enum:
			RETRO_DEVICE_ID_JOYPAD_B      =  0
			RETRO_DEVICE_ID_JOYPAD_Y      =  1
			RETRO_DEVICE_ID_JOYPAD_SELECT =  2
			RETRO_DEVICE_ID_JOYPAD_START  =  3
			RETRO_DEVICE_ID_JOYPAD_UP     =  4
			RETRO_DEVICE_ID_JOYPAD_DOWN   =  5
			RETRO_DEVICE_ID_JOYPAD_LEFT   =  6
			RETRO_DEVICE_ID_JOYPAD_RIGHT  =  7
			RETRO_DEVICE_ID_JOYPAD_A      =  8
			RETRO_DEVICE_ID_JOYPAD_X      =  9
			RETRO_DEVICE_ID_JOYPAD_L      = 10
			RETRO_DEVICE_ID_JOYPAD_R      = 11
			RETRO_DEVICE_ID_JOYPAD_L2     = 12
			RETRO_DEVICE_ID_JOYPAD_R2     = 13
			RETRO_DEVICE_ID_JOYPAD_L3     = 14
			RETRO_DEVICE_ID_JOYPAD_R3     = 15

		enum:
			RETRO_DEVICE_INDEX_ANALOG_LEFT  = 0
			RETRO_DEVICE_INDEX_ANALOG_RIGHT = 1
			RETRO_DEVICE_ID_ANALOG_X        = 0
			RETRO_DEVICE_ID_ANALOG_Y        = 1
		enum:
			RETRO_DEVICE_ID_MOUSE_X     = 0
			RETRO_DEVICE_ID_MOUSE_Y     = 1
			RETRO_DEVICE_ID_MOUSE_LEFT  = 2
			RETRO_DEVICE_ID_MOUSE_RIGHT = 3
		enum:
			RETRO_DEVICE_ID_LIGHTGUN_X       = 0
			RETRO_DEVICE_ID_LIGHTGUN_Y       = 1
			RETRO_DEVICE_ID_LIGHTGUN_TRIGGER = 2
			RETRO_DEVICE_ID_LIGHTGUN_CURSOR  = 3
			RETRO_DEVICE_ID_LIGHTGUN_TURBO   = 4
			RETRO_DEVICE_ID_LIGHTGUN_PAUSE   = 5
			RETRO_DEVICE_ID_LIGHTGUN_START   = 6
		enum:
			RETRO_REGION_NTSC = 0
			RETRO_REGION_PAL  = 1
		enum:
			RETRO_MEMORY_MASK       = 0xff
			RETRO_MEMORY_SAVE_RAM   = 0
			RETRO_MEMORY_RTC        = 1
			RETRO_MEMORY_SYSTEM_RAM = 2
			RETRO_MEMORY_VIDEO_RAM  = 3
		enum:
			RETRO_MEMORY_SNES_BSX_RAM            = ((1 << 8) | RETRO_MEMORY_SAVE_RAM)
			RETRO_MEMORY_SNES_BSX_PRAM           = ((2 << 8) | RETRO_MEMORY_SAVE_RAM)
			RETRO_MEMORY_SNES_SUFAMI_TURBO_A_RAM = ((3 << 8) | RETRO_MEMORY_SAVE_RAM)
			RETRO_MEMORY_SNES_SUFAMI_TURBO_B_RAM = ((4 << 8) | RETRO_MEMORY_SAVE_RAM)
			RETRO_MEMORY_SNES_GAME_BOY_RAM       = ((5 << 8) | RETRO_MEMORY_SAVE_RAM)
			RETRO_MEMORY_SNES_GAME_BOY_RTC       = ((6 << 8) | RETRO_MEMORY_RTC)
		enum:
			RETRO_GAME_TYPE_BSX            = 0x101
			RETRO_GAME_TYPE_BSX_SLOTTED    = 0x102
			RETRO_GAME_TYPE_SUFAMI_TURBO   = 0x103
			RETRO_GAME_TYPE_SUPER_GAME_BOY = 0x104
		enum:
			RETRO_ENVIRONMENT_SET_ROTATION          =  1
			RETRO_ENVIRONMENT_GET_OVERSCAN          =  2
			RETRO_ENVIRONMENT_GET_CAN_DUPE          =  3
			RETRO_ENVIRONMENT_GET_VARIABLE          =  4
			RETRO_ENVIRONMENT_SET_VARIABLES         =  5
			RETRO_ENVIRONMENT_SET_MESSAGE           =  6
			RETRO_ENVIRONMENT_SHUTDOWN              =  7
			RETRO_ENVIRONMENT_SET_PERFORMANCE_LEVEL =  8
			RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY  =  9
			RETRO_ENVIRONMENT_SET_PIXEL_FORMAT      = 10


		enum retro_pixel_format:
			RETRO_PIXEL_FORMAT_0RGB1555 = 0
			RETRO_PIXEL_FORMAT_XRGB8888 = 1

		struct retro_message:
			char*    msg
			unsigned frames

		struct retro_system_info:
			char* library_name
			char* library_version
			char* valid_extensions
			bool  need_fullpath
			bool  block_extract

		struct retro_game_geometry:
			unsigned base_width
			unsigned base_height
			unsigned max_width
			unsigned max_height
			float    aspect_ratio

		struct retro_system_timing:
			double fps
			double sample_rate

		struct retro_system_av_info:
			retro_game_geometry geometry
			retro_system_timing timing

		struct retro_variable:
			char* key
			char* value

		struct retro_game_info:
			char*  path
			void*  data
			size_t size
			char*  meta

ctypedef bool (*environment_t)(unsigned cmd, void* data)

ctypedef void (*video_refresh_t)(void* data, unsigned width, unsigned height, size_t pitch)
ctypedef void (*audio_sample_t)(int16_t left, int16_t right)
ctypedef size_t (*audio_sample_batch_t)(int16_t* data, size_t frames)
ctypedef void (*input_poll_t)()
ctypedef int16_t (*input_state_t)(unsigned port, unsigned device, unsigned index, unsigned id)

ctypedef void (*set_environment_t)(environment_t)
ctypedef void (*set_video_refresh_t)(video_refresh_t cb)
ctypedef void (*set_audio_sample_t)(audio_sample_t cb)
ctypedef void (*set_audio_sample_batch_t)(audio_sample_batch_t cb)
ctypedef void (*set_input_poll_t)(input_poll_t cb)
ctypedef void (*set_input_state_t)(input_state_t cb)

ctypedef void (*init_t)()
ctypedef void (*deinit_t)()

ctypedef unsigned (*api_version_t)()

ctypedef void (*get_system_info_t)(retro_system_info* info)
ctypedef void (*get_system_av_info_t)(retro_system_av_info* info)

ctypedef void (*set_controller_port_device_t)(unsigned port, unsigned device)

ctypedef void (*reset_t)()
ctypedef void (*run_t)()

ctypedef size_t (*serialize_size_t)()
ctypedef bool (*serialize_t)(void* data, size_t size)
ctypedef bool (*unserialize_t)(void* data, size_t size)

ctypedef void (*cheat_reset_t)()
ctypedef void (*cheat_set_t)(unsigned index, bool enabled, char* code)

ctypedef bool (*load_game_t)(retro_game_info* game)
ctypedef bool (*load_game_special_t)(unsigned game_type, retro_game_info* info, size_t num_info)
ctypedef void (*unload_game_t)()

ctypedef unsigned (*get_region_t)()

ctypedef void*  (*get_memory_data_t)(unsigned id)
ctypedef size_t (*get_memory_size_t)(unsigned id)

cdef nogil:
	void null_video_refresh(void* data, unsigned width, unsigned height, size_t pitch)
	void null_audio_sample(int16_t left, int16_t right)
	size_t null_audio_sample_batch(int16_t* data, size_t frames)
	void null_input_poll()
	int16_t null_input_state(unsigned port, unsigned device, unsigned index, unsigned id)

# extension types
cdef class LowLevelWrapper:
	cdef public char* error
	cdef nogil:
		void* handle

		set_environment_t        set_environment
		set_video_refresh_t      set_video_refresh
		set_audio_sample_t       set_audio_sample
		set_audio_sample_batch_t set_audio_sample_batch
		set_input_poll_t         set_input_poll
		set_input_state_t        set_input_state

		init_t   init
		deinit_t deinit

		api_version_t api_version

		get_system_info_t    get_system_info
		get_system_av_info_t get_system_av_info

		set_controller_port_device_t set_controller_port_device

		reset_t reset
		run_t   run

		serialize_size_t serialize_size
		serialize_t      serialize
		unserialize_t    unserialize

		cheat_reset_t cheat_reset
		cheat_set_t   cheat_set

		load_game_t         load_game
		load_game_special_t load_game_special
		unload_game_t       unload_game

		get_region_t get_region

		get_memory_data_t get_memory_data
		get_memory_size_t get_memory_size

cdef class EmulatedSystem:
	cdef nogil:
		LowLevelWrapper llw
		retro_system_av_info av_info
		bool _game_loaded
	cdef dict _loaded_cheats
	cpdef _require_game_not_loaded(self)
	cpdef _require_game_loaded(self)
	cpdef set_controller_port_device(self, unsigned port, unsigned device)
	cpdef reset(self)
	cpdef run(self, int frames=?)
	cpdef unload(self)
	cpdef get_refresh_rate(self)
	cpdef serialize(self)
	cpdef unserialize(self, bytes state)
	cpdef get_library_info(self)
	cpdef get_av_info(self)
	cpdef close(self)
	cdef public void set_null_callbacks(self)

cdef class EmulatedSNES(EmulatedSystem):
	pass

