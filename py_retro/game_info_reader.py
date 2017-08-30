import ctypes
module_name = "get_game_info"

class GameInfoReader:
    coreToRomType = {
        'gambatte': 'gbc'
    }

    def get_gbc_game_info(self, data):
        return {
            'name': ctypes.string_at(data[0x134:0x143]).decode('utf-8')
        }

    def get_info(self, romData, coreName):
        romType = self.coreToRomType.get(coreName.lower())
        if romType == None:
            print("Couldn't get game info because the core '{}' is unknown.".format(coreName))
            return {}

        getInfoForCore = getattr(self, "get_{}_game_info".format(romType))
        if getInfoForCore == None:
            print("Couldn't get game info since the rom type '{}' is unknown.".format(romType))
            return {}

        return getInfoForCore(romData)
