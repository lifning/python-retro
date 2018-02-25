import ctypes

from .retro_ctypes import retro_environment_t, retro_video_refresh_t, retro_audio_sample_t, \
    retro_audio_sample_batch_t, retro_input_poll_t, retro_input_state_t, retro_system_info, retro_system_av_info, \
    retro_game_info


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
        self.retro_cheat_set.argtypes = [ctypes.c_uint, ctypes.c_bool, ctypes.c_char_p]

        self.retro_load_game.restype = ctypes.c_bool
        self.retro_load_game.argtypes = [ctypes.POINTER(retro_game_info)]

        self.retro_load_game_special.restype = ctypes.c_bool
        self.retro_load_game_special.argtypes = [ctypes.c_uint,
                                                 ctypes.POINTER(retro_game_info),
                                                 ctypes.c_size_t]

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
