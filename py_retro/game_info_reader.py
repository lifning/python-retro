import collections
import ctypes
import sys

from py_retro.api import ENVIRONMENT_SET_MEMORY_MAPS, retro_memory_map, MEMORY_SYSTEM_RAM
from py_retro.core import EmulatedSystem, TraceStubMixin

module_name = 'get_game_info'


class GameInfoReader:
    core_to_rom_type = {
        'gambatte': 'gbc',
        'bsnes': 'snes',
        'genesis plus gx': 'genesis',
        'higan (super famicom accuracy)': 'snes',
    }

    @staticmethod
    def get_gbc_game_info(data):
        return {
            'name': ctypes.string_at(data[0x134:0x143]).decode('ascii').rstrip()
        }

    @staticmethod
    def get_snes_game_info(data):
        return {
            'name': ctypes.string_at(data[0x7fC0:0x7fD5]).decode('ascii').rstrip()
        }

    @staticmethod
    def get_genesis_game_info(data):
        return {
            'name': ' '.join(ctypes.string_at(data[0x120:0x150]).decode('ascii').split())
        }

    def get_info(self, rom_data, core_name):
        rom_type = self.core_to_rom_type.get(core_name.lower())
        if rom_type is None:
            print(f'py_retro: Could not get game info because the core "{core_name}" is unknown.',
                  file=sys.stderr)
            return {}

        get_info_for_core = getattr(self, f'get_{rom_type}_game_info')
        if get_info_for_core is None:
            print(f'py_retro: Could not get game info since the ROM type "{rom_type}" is unknown.',
                  file=sys.stderr)
            return {}

        value = get_info_for_core(rom_data)
        print(value)
        return value


class MemoryOpsMixin(EmulatedSystem):
    """ This mixin includes methods useful for inspecting and manipulating the state of the emulated console's memory,
    including work RAM, save RAM, and ROM, via either direct programmatic access or using `retro_cheat_set`.
    """
    def __init__(self, libpath, **kw):
        super().__init__(libpath, **kw)
        self._loaded_cheats = {}
        # simple default WRAM-only address space if the env isn't called
        self.memory_map = collections.OrderedDict()
        self.game_info = None

    def load_game(self, data=None, path=None, meta=None, get_data_from_path=True):
        super().load_game(data, path, meta, get_data_from_path)
        # get useful info about the game from the rom's header
        if self.game_data is not None:
            self.game_info = GameInfoReader().get_info(self.game_data, self.name)

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
        return super()._environment(cmd, data)

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
