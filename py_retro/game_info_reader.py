import ctypes
import sys

module_name = 'get_game_info'


class GameInfoReader:
    coreToRomType = {
        'gambatte': 'gbc',
        'bsnes': 'snes',
        'genesis plus gx': 'genesis',
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
        rom_type = self.coreToRomType.get(core_name.lower())
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
