import os

import collections

from .game_info_reader import GameInfoReader

from .retro_functions import *
from .retro_constants import *


# try to load C helper library
wrapped_retro_log_print_t = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p)
_log_wrapper_mod = None
# noinspection PyBroadException
try:
    _log_wrapper_mod = ctypes.CDLL(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'c_ext', 'log_wrapper.so')
    )
    _log_wrapper_mod.handle_env_get_log_interface_restype = None
    _log_wrapper_mod.handle_env_get_log_interface_argtypes = [
        ctypes.POINTER(retro_log_callback),
        wrapped_retro_log_print_t
    ]
except Exception as ex:
    print(f'Could not load variadic log wrapper module: {repr(ex)}')


class SerializationError(Exception):
    pass


class LoadGameError(Exception):
    pass


class EmulatedSystem:
    def __init__(self, libpath, **kw):
        self.llw = LowLevelWrapper(libpath)
        self.name = self.get_library_info()['name']

        # HACK: just put this in for software frames 'til we support SET_HW_RENDER
        self.env_vars = {b'parallel-n64-gfxplugin': b'angrylion'}

        # todo: a layer of indirection to allow live monkey-patching?
        self._video_refresh_wrapper = retro_video_refresh_t(self._video_refresh)
        self._audio_sample_wrapper = retro_audio_sample_t(self._audio_sample)
        self._audio_sample_batch_wrapper = retro_audio_sample_batch_t(self._audio_sample_batch)
        self._input_poll_wrapper = retro_input_poll_t(self._input_poll)
        self._input_state_wrapper = retro_input_state_t(self._input_state)
        self._environment_wrapper = retro_environment_t(self._environment)
        self._log_wrapper = wrapped_retro_log_print_t(self._log)

        self.llw.set_video_refresh(self._video_refresh_wrapper)
        self.llw.set_audio_sample_batch(self._audio_sample_batch_wrapper)
        # todo: see if we can unconditionally set both without negative consequence.
        # we really don't want non-batch being called if we can help it, because it's very slow
        if HACK_need_audio_sample(self.name):
            self.llw.set_audio_sample(self._audio_sample_wrapper)
        self.llw.set_input_poll(self._input_poll_wrapper)
        self.llw.set_input_state(self._input_state_wrapper)
        self.llw.set_environment(self._environment_wrapper)

        self.llw.init()
        self.av_info = retro_system_av_info()

    def __del__(self):
        self.llw.deinit()

    def __set_geometry_wrapper(self) -> bool:
        return self._set_geometry(
            base_size=(int(self.av_info.geometry.base_width), int(self.av_info.geometry.base_height)),
            max_size=(int(self.av_info.geometry.max_width), int(self.av_info.geometry.max_height)),
            aspect_ratio=float(self.av_info.geometry.aspect_ratio)
        )

    def __set_timing_wrapper(self) -> bool:
        return self._set_timing(
            fps=float(self.av_info.timing.fps),
            sample_rate=float(self.av_info.timing.sample_rate)
        )

    def get_library_info(self):
        info = retro_system_info()
        self.llw.get_system_info(ctypes.byref(info))
        return {
            'api': int(self.llw.api_version()),
            'name': info.library_name.decode("utf-8"),
            'ver': info.library_version.decode("utf-8"),
            'exts': info.valid_extensions.decode("utf-8"),
        }

    def load_game(self, data=None, path=None, meta=None, get_data_from_path=True):
        game_info = retro_game_info()
        system_info = retro_system_info()

        self.llw.get_system_info(ctypes.byref(system_info))

        if path:
            if isinstance(path, str):
                path = path.encode('utf-8')

            game_info.path = ctypes.cast(path, ctypes.c_char_p)
            if get_data_from_path and not data:
                data = open(path, 'rb').read()

        if meta:
            if isinstance(meta, str):
                meta = meta.encode('utf-8')
            game_info.meta = ctypes.cast(meta, ctypes.c_char_p)

        elif system_info.need_fullpath:
            raise LoadGameError(f'{self.name} needs a full path to the game file.')

        if data:
            game_info.data = ctypes.cast(data, ctypes.c_void_p)
            game_info.size = len(data)
        elif not path:
            raise LoadGameError('Must provide either file path or raw loaded game!')

        self.llw.load_game(ctypes.byref(game_info))
        self.llw.get_system_av_info(ctypes.byref(self.av_info))
        self.__set_geometry_wrapper()
        self.__set_timing_wrapper()

    def unload(self):
        self.llw.unload_game()

    def serialize(self) -> bytes:
        size = self.llw.serialize_size()
        buf = ctypes.create_string_buffer(size)
        res = self.llw.serialize(ctypes.cast(buf, ctypes.c_void_p), size)
        if not res:
            raise SerializationError('problem in serialize')
        return buf.raw

    def unserialize(self, state: bytes):
        res = self.llw.unserialize(ctypes.cast(state, ctypes.c_void_p), len(state))
        if not res:
            raise SerializationError('problem in unserialize')

    def set_controller_port_device(self, port: int, device: int):
        self.llw.set_controller_port_device(port, device)

    def reset(self):
        self.llw.reset()

    def run(self):
        self.llw.run()

    def _environment(self, cmd: int, data: ctypes.c_void_p) -> bool:
        if cmd == ENVIRONMENT_GET_CAN_DUPE:
            b_data = ctypes.cast(data, ctypes.POINTER(ctypes.c_bool))
            b_data[0] = True
            return True

        elif cmd == ENVIRONMENT_SET_PIXEL_FORMAT:
            return self._set_pixel_format(ctypes.cast(data, ctypes.POINTER(ctypes.c_int))[0])

        elif cmd == ENVIRONMENT_GET_VARIABLE:
            variable = ctypes.cast(data, ctypes.POINTER(retro_variable))[0]
            variable.value = self.env_vars.get(variable.key)
            return True

        elif cmd == ENVIRONMENT_SET_VARIABLES:
            variables = ctypes.cast(data, ctypes.POINTER(retro_variable))
            idx = 0
            current = variables[idx]

            while current.key is not None:
                description, _, options = current.value.partition(b'; ')
                options = options.split(b'|')
                val = self.env_vars.setdefault(current.key, options[0])
                assert val in options, f'{val} invalid for {current.key}, expected {options}'
                idx += 1
                current = variables[idx]
            return True

        elif cmd == ENVIRONMENT_GET_VARIABLE_UPDATE:
            b_data = ctypes.cast(data, ctypes.POINTER(ctypes.c_bool))
            b_data[0] = False  # assumption: we will never change variables after launched
            return True

        elif cmd == ENVIRONMENT_SET_SYSTEM_AV_INFO:
            ctypes.memmove(ctypes.byref(self.av_info),
                           ctypes.cast(data, ctypes.POINTER(retro_system_av_info)),
                           ctypes.sizeof(retro_system_av_info))
            return self.__set_geometry_wrapper() and self.__set_timing_wrapper()

        elif cmd == ENVIRONMENT_SET_GEOMETRY:
            ctypes.memmove(ctypes.byref(self.av_info.geometry),
                           ctypes.cast(data, ctypes.POINTER(retro_game_geometry)),
                           ctypes.sizeof(retro_game_geometry))
            return self.__set_geometry_wrapper()

        elif cmd == ENVIRONMENT_GET_SYSTEM_DIRECTORY:
            path = self._get_system_directory()
            if os.path.isdir(path):
                p_path = ctypes.cast(data, ctypes.POINTER(ctypes.c_char_p))
                p_path[0] = ctypes.cast(path, ctypes.c_char_p)
                return True
            return False

        elif cmd == ENVIRONMENT_GET_SAVE_DIRECTORY:
            path = self._get_save_directory()
            if os.path.isdir(path):
                p_path = ctypes.cast(data, ctypes.POINTER(ctypes.c_char_p))
                p_path[0] = ctypes.cast(path, ctypes.c_char_p)
                return True
            return False

        elif cmd == ENVIRONMENT_GET_LOG_INTERFACE:
            if _log_wrapper_mod is not None:
                _log_wrapper_mod.handle_env_get_log_interface(
                    ctypes.cast(data, ctypes.POINTER(retro_log_callback)), self._log_wrapper)
                return True
            else:
                print('environment: could not set logging interface because C wrapper not loaded.')
                return False

        print(f'retro_environment not implemented: {rcl("ENVIRONMENT", cmd)}')
        return False

    def _log(self, level: int, msg: ctypes.c_char_p):
        level_name = ''.join(rcl('LOG', level))
        print(f'[{level_name}] {ctypes.string_at(msg).decode("utf-8").rstrip()}')

    def _video_refresh(self, data: ctypes.c_void_p, width: int, height: int, pitch: int):
        pass

    def _audio_sample(self, left: int, right: int):
        pass

    def _audio_sample_batch(self, data: ctypes.c_void_p, frames: int) -> int:
        return frames

    def _input_poll(self):
        pass

    def _input_state(self, port: int, device: int, index: int, id_: int) -> int:
        return 0

    def _get_system_directory(self) -> str:
        return ''

    def _get_save_directory(self) -> str:
        return ''

    def _set_geometry(self, base_size: tuple, max_size: tuple, aspect_ratio: float) -> bool:
        return True

    def _set_timing(self, fps: float, sample_rate: float) -> bool:
        return True

    def _set_pixel_format(self, fmt: int) -> bool:
        return True


class TraceStubMixin(EmulatedSystem):
    def _video_refresh(self, data: ctypes.c_void_p, width: int, height: int, pitch: int):
        print(f'video_refresh(data={id(data)}, width={width}, height={height}, pitch={pitch})')
        super()._video_refresh(data, width, height, pitch)

    def _audio_sample(self, left: int, right: int):
        print(f'audio_sample(left={left}, right={right})')
        super()._audio_sample(left, right)

    def _audio_sample_batch(self, data: ctypes.c_void_p, frames: int) -> int:
        print(f'audio_sample_batch(data={id(data)}, frames={frames})')
        return super()._audio_sample_batch(data, frames)

    def _input_poll(self):
        print('input_poll()')
        super()._input_poll()

    def _input_state(self, port: int, device: int, index: int, id_: int) -> int:
        print(f'input_state(port={port}, '
              f'device={rcl("DEVICE", device)}, '
              f'index={rcl("DEVICE_INDEX", index)}, '
              f'id={rcl("DEVICE_ID", id_)})')
        return super()._input_state(port, device, index, id_)

    def _get_system_directory(self) -> str:
        print(f'get_system_directory()')
        return super()._get_system_directory()

    def _get_save_directory(self) -> str:
        print(f'get_save_directory()')
        return super()._get_save_directory()

    def _set_geometry(self, base_size: tuple, max_size: tuple, aspect_ratio: float) -> bool:
        print(f'set_geometry(base_size={base_size}, max_size={max_size}, aspect_ratio={aspect_ratio})')
        return super()._set_geometry(base_size, max_size, aspect_ratio)

    def _set_timing(self, fps: float, sample_rate: float) -> bool:
        print(f'set_timing(fps={fps}, sample_rate={sample_rate})')
        return super()._set_timing(fps, sample_rate)

    def _set_pixel_format(self, fmt: int) -> bool:
        print(f'set_pixel_format(fmt={rcl("PIXEL", fmt)})')
        return super()._set_pixel_format(fmt)


class MemoryOpsMixin(EmulatedSystem):
    def __init__(self, libpath, **kw):
        super().__init__(libpath, **kw)
        self._loaded_cheats = {}
        # simple default WRAM-only address space if the env isn't called
        self.memory_map = collections.OrderedDict()
        self.game_info = None

    def load_game(self, data=None, path=None, meta=None, get_data_from_path=True):
        super().load_game(data, path, meta, get_data_from_path)
        # get useful info about the game from the rom's header
        self.game_info = GameInfoReader().get_info(data, self.name)

    def _environment(self, cmd: int, data: ctypes.c_void_p) -> bool:
        if cmd == ENVIRONMENT_SET_MEMORY_MAPS:
            # FIXME: partial implementation good enough for Gambatte
            maps = ctypes.cast(data, ctypes.POINTER(retro_memory_map))
            desc_list = []
            for i in range(maps[0].num_descriptors):
                desc = maps[0].descriptors[i]
                length = desc.len
                if desc.select:  # FIXME: hack for oversized SRAM eating addr space...
                    length = (~desc.select + 1) & 0xffffffff
                    print(f'truncating memory region {hex(desc.start)} from size {hex(desc.len)} '
                          f'to {desc.len//length} banks of size {hex(length)}')
                desc_list.append(((desc.start, desc.start + length), desc.ptr))
            desc_list.sort()
            self.memory_map = collections.OrderedDict(desc_list)
            if isinstance(self, TraceStubMixin):
                print(self.memory_map)
            return True
        super()._environment(cmd, data)

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

    def _reload_cheats(self):
        """ Internal method.
        Reloads cheats in the emulated console from the _loaded_cheats variable.
        """
        self.llw.cheat_reset()
        for index, (code, enabled) in list(self._loaded_cheats.items()):
            self.llw.cheat_set(index, enabled, code)

    def __find_memory_bank(self, offset: int, length: int, bank_switch: int) -> ctypes.c_void_p:
        if not self.memory_map:
            mem_size = self.llw.get_memory_size(MEMORY_SYSTEM_RAM)
            mem_data = self.llw.get_memory_data(MEMORY_SYSTEM_RAM)
            self.memory_map[(0, mem_size)] = mem_data
        for (begin, end), pointer in self.memory_map.items():
            if begin <= offset < end:
                if offset + length > end:
                    raise IndexError(f'({hex(offset)}, {hex(length)}) '
                                     f'overruns ({hex(begin)}, {hex(end)}) memory bank')
                bank_size = end - begin
                relative_offset = offset - begin + (bank_size * bank_switch)
                return pointer + relative_offset
        raise IndexError(f'({hex(offset)}, {hex(length)}) '
                         'address range not found in any memory map region')

    def peek_memory_region(self, offset: int, length: int, bank_switch: int = 0) -> bytes:
        pointer = self.__find_memory_bank(offset, length, bank_switch)
        buffer = ctypes.create_string_buffer(length)
        ctypes.memmove(buffer, pointer, length)
        return buffer.raw

    def poke_memory_region(self, offset: int, data: bytes, bank_switch: int = 0):
        pointer = self.__find_memory_bank(offset, len(data), bank_switch)
        ctypes.memmove(pointer, data, len(data))

    def memory_to_string(self, mem_type: int):
        """
        Copies data from the given libretro memory buffer into a new string.
        """
        mem_size = self.llw.get_memory_size(mem_type)
        mem_data = self.llw.get_memory_data(mem_type)

        if mem_size == 0:
            return None

        buf = ctypes.create_string_buffer(mem_size)
        ctypes.memmove(buf, mem_data, mem_size)

        return buf.raw

    def string_to_memory(self, data, mem_type):
        """
        Copies the given data into the libretro memory buffer of the given type.
        """
        mem_size = self.llw.get_memory_size(mem_type)
        mem_data = self.llw.get_memory_data(mem_type)

        if len(data) != mem_size:
            raise ValueError(
                "This game requires {} bytes of memory type {}, not {} bytes".format(
                    mem_size, mem_type, len(data)
                )
            )
        ctypes.memmove(mem_data, data, mem_size)
