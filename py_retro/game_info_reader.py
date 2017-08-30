import ctypes
module_name = "get_game_info"

class GameInfoReader:
    def get_gambatte_game_info(self, data):
        return {
            'name': ctypes.string_at(data[0x134:0x143])
        }

    def get_info(self, romData, coreName):
        getInfoForCore = getattr(self, "get_{}_game_info".format(coreName.lower()))
        if getInfoForCore == None:
            print("Couldn't get game info since the core '{}' is unknown.".format(coreName))
            return {}
        return getInfoForCore(romData)
