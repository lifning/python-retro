from .retro_ctypes import *


# workarounds
def HACK_need_audio_sample_batch(name):
    for x in ['FCEUmm', 'Gambatte', 'Genesis Plus GX', 'SNES9x', 'VBA Next']:
        if name.startswith(x):
            return True
    return False


def HACK_need_audio_sample(name):
    for x in ['bNES', 'bSNES', 'Meteor GBA', 'higan', 'nSide']:
        if name.startswith(x):
            return True
    return False


# constants
DEVICE_TYPE_SHIFT = 8
DEVICE_MASK = ((1 << DEVICE_TYPE_SHIFT) - 1)
DEVICE_SUBCLASS = lambda base, id: (((id + 1) << DEVICE_TYPE_SHIFT) | base)

DEVICE_NONE = 0
DEVICE_JOYPAD = 1
DEVICE_MOUSE = 2
DEVICE_KEYBOARD = 3
DEVICE_LIGHTGUN = 4
DEVICE_ANALOG = 5
DEVICE_POINTER = 6

DEVICE_JOYPAD_MULTITAP = ((1 << 8) | DEVICE_JOYPAD)
DEVICE_LIGHTGUN_SUPER_SCOPE = ((1 << 8) | DEVICE_LIGHTGUN)
DEVICE_LIGHTGUN_JUSTIFIER = ((2 << 8) | DEVICE_LIGHTGUN)
DEVICE_LIGHTGUN_JUSTIFIERS = ((3 << 8) | DEVICE_LIGHTGUN)

DEVICE_ID_JOYPAD_B = 0
DEVICE_ID_JOYPAD_Y = 1
DEVICE_ID_JOYPAD_SELECT = 2
DEVICE_ID_JOYPAD_START = 3
DEVICE_ID_JOYPAD_UP = 4
DEVICE_ID_JOYPAD_DOWN = 5
DEVICE_ID_JOYPAD_LEFT = 6
DEVICE_ID_JOYPAD_RIGHT = 7
DEVICE_ID_JOYPAD_A = 8
DEVICE_ID_JOYPAD_X = 9
DEVICE_ID_JOYPAD_L = 10
DEVICE_ID_JOYPAD_R = 11
DEVICE_ID_JOYPAD_L2 = 12
DEVICE_ID_JOYPAD_R2 = 13
DEVICE_ID_JOYPAD_L3 = 14
DEVICE_ID_JOYPAD_R3 = 15

DEVICE_INDEX_ANALOG_LEFT = 0
DEVICE_INDEX_ANALOG_RIGHT = 1
DEVICE_INDEX_ANALOG_BUTTON = 2
DEVICE_ID_ANALOG_X = 0
DEVICE_ID_ANALOG_Y = 1

DEVICE_ID_MOUSE_X = 0
DEVICE_ID_MOUSE_Y = 1
DEVICE_ID_MOUSE_LEFT = 2
DEVICE_ID_MOUSE_RIGHT = 3
DEVICE_ID_MOUSE_WHEELUP = 4
DEVICE_ID_MOUSE_WHEELDOWN = 5
DEVICE_ID_MOUSE_MIDDLE = 6
DEVICE_ID_MOUSE_HORIZ_WHEELUP = 7
DEVICE_ID_MOUSE_HORIZ_WHEELDOWN = 8
DEVICE_ID_MOUSE_BUTTON_4 = 9
DEVICE_ID_MOUSE_BUTTON_5 = 10

DEVICE_ID_LIGHTGUN_SCREEN_X = 13
DEVICE_ID_LIGHTGUN_SCREEN_Y = 14
DEVICE_ID_LIGHTGUN_IS_OFFSCREEN = 15
DEVICE_ID_LIGHTGUN_TRIGGER = 2
DEVICE_ID_LIGHTGUN_RELOAD = 16
DEVICE_ID_LIGHTGUN_AUX_A = 3
DEVICE_ID_LIGHTGUN_AUX_B = 4
DEVICE_ID_LIGHTGUN_START = 6
DEVICE_ID_LIGHTGUN_SELECT = 7
DEVICE_ID_LIGHTGUN_AUX_C = 8
DEVICE_ID_LIGHTGUN_DPAD_UP = 9
DEVICE_ID_LIGHTGUN_DPAD_DOWN = 10
DEVICE_ID_LIGHTGUN_DPAD_LEFT = 11
DEVICE_ID_LIGHTGUN_DPAD_RIGHT = 12

DEVICE_ID_LIGHTGUN_X = 0
DEVICE_ID_LIGHTGUN_Y = 1
DEVICE_ID_LIGHTGUN_CURSOR = 3
DEVICE_ID_LIGHTGUN_TURBO = 4
DEVICE_ID_LIGHTGUN_PAUSE = 5

DEVICE_ID_POINTER_X = 0
DEVICE_ID_POINTER_Y = 1
DEVICE_ID_POINTER_PRESSED = 2

REGION_NTSC = 0
REGION_PAL = 1

LANGUAGE_ENGLISH = 0
LANGUAGE_JAPANESE = 1
LANGUAGE_FRENCH = 2
LANGUAGE_SPANISH = 3
LANGUAGE_GERMAN = 4
LANGUAGE_ITALIAN = 5
LANGUAGE_DUTCH = 6
LANGUAGE_PORTUGUESE_BRAZIL = 7
LANGUAGE_PORTUGUESE_PORTUGAL = 8
LANGUAGE_RUSSIAN = 9
LANGUAGE_KOREAN = 10
LANGUAGE_CHINESE_TRADITIONAL = 11
LANGUAGE_CHINESE_SIMPLIFIED = 12
LANGUAGE_ESPERANTO = 13
LANGUAGE_POLISH = 14
LANGUAGE_VIETNAMESE = 15
LANGUAGE_LAST = 16

MEMORY_MASK = 0xff
MEMORY_SAVE_RAM = 0
MEMORY_RTC = 1
MEMORY_SYSTEM_RAM = 2
MEMORY_VIDEO_RAM = 3

MEMORY_SNES_BSX_RAM = ((1 << 8) | MEMORY_SAVE_RAM)
MEMORY_SNES_BSX_PRAM = ((2 << 8) | MEMORY_SAVE_RAM)
MEMORY_SNES_SUFAMI_TURBO_A_RAM = ((3 << 8) | MEMORY_SAVE_RAM)
MEMORY_SNES_SUFAMI_TURBO_B_RAM = ((4 << 8) | MEMORY_SAVE_RAM)
MEMORY_SNES_GAME_BOY_RAM = ((5 << 8) | MEMORY_SAVE_RAM)
MEMORY_SNES_GAME_BOY_RTC = ((6 << 8) | MEMORY_RTC)

GAME_TYPE_BSX = 0x101
GAME_TYPE_BSX_SLOTTED = 0x102
GAME_TYPE_SUFAMI_TURBO = 0x103
GAME_TYPE_SUPER_GAME_BOY = 0x104

ENVIRONMENT_EXPERIMENTAL = 0x10000
ENVIRONMENT_PRIVATE = 0x20000

ENVIRONMENT_SET_ROTATION = 1
ENVIRONMENT_GET_OVERSCAN = 2
ENVIRONMENT_GET_CAN_DUPE = 3
# Moved to 15 and 16
# ENVIRONMENT_GET_VARIABLE = 4
# ENVIRONMENT_SET_VARIABLES = 5
ENVIRONMENT_SET_MESSAGE = 6
ENVIRONMENT_SHUTDOWN = 7
ENVIRONMENT_SET_PERFORMANCE_LEVEL = 8
ENVIRONMENT_GET_SYSTEM_DIRECTORY = 9
ENVIRONMENT_SET_PIXEL_FORMAT = 10

PIXEL_FORMAT_0RGB1555 = 0
PIXEL_FORMAT_XRGB8888 = 1
PIXEL_FORMAT_RGB565 = 2

ENVIRONMENT_SET_INPUT_DESCRIPTORS = 11
ENVIRONMENT_SET_KEYBOARD_CALLBACK = 12
ENVIRONMENT_SET_DISK_CONTROL_INTERFACE = 13
ENVIRONMENT_SET_HW_RENDER = 14
ENVIRONMENT_GET_VARIABLE = 15
ENVIRONMENT_SET_VARIABLES = 16
ENVIRONMENT_GET_VARIABLE_UPDATE = 17
ENVIRONMENT_SET_SUPPORT_NO_GAME = 18
ENVIRONMENT_GET_LIBRETRO_PATH = 19
# 20 was an obsolete version of SET_AUDIO_CALLBACK
ENVIRONMENT_SET_FRAME_TIME_CALLBACK = 21
ENVIRONMENT_SET_AUDIO_CALLBACK = 22
ENVIRONMENT_GET_RUMBLE_INTERFACE = 23
ENVIRONMENT_GET_INPUT_DEVICE_CAPABILITIES = 24
ENVIRONMENT_GET_SENSOR_INTERFACE = (25 | ENVIRONMENT_EXPERIMENTAL)
ENVIRONMENT_GET_CAMERA_INTERFACE = (26 | ENVIRONMENT_EXPERIMENTAL)
ENVIRONMENT_GET_LOG_INTERFACE = 27
ENVIRONMENT_GET_PERF_INTERFACE = 28
ENVIRONMENT_GET_LOCATION_INTERFACE = 29
ENVIRONMENT_GET_CORE_ASSETS_DIRECTORY = 30
ENVIRONMENT_GET_SAVE_DIRECTORY = 31
ENVIRONMENT_SET_SYSTEM_AV_INFO = 32
ENVIRONMENT_SET_PROC_ADDRESS_CALLBACK = 33
ENVIRONMENT_SET_SUBSYSTEM_INFO = 34
ENVIRONMENT_SET_CONTROLLER_INFO = 35
ENVIRONMENT_SET_MEMORY_MAPS = (36 | ENVIRONMENT_EXPERIMENTAL)

MEMDESC_CONST = (1 << 0)
MEMDESC_BIGENDIAN = (1 << 1)
MEMDESC_ALIGN_2 = (1 << 16)
MEMDESC_ALIGN_4 = (2 << 16)
MEMDESC_ALIGN_8 = (3 << 16)
MEMDESC_MINSIZE_2 = (1 << 24)
MEMDESC_MINSIZE_4 = (2 << 24)
MEMDESC_MINSIZE_8 = (3 << 24)

ENVIRONMENT_SET_GEOMETRY = 37
ENVIRONMENT_GET_USERNAME = 38
ENVIRONMENT_GET_LANGUAGE = 39
ENVIRONMENT_GET_CURRENT_SOFTWARE_FRAMEBUFFER = (40 | ENVIRONMENT_EXPERIMENTAL)
ENVIRONMENT_GET_HW_RENDER_INTERFACE = (41 | ENVIRONMENT_EXPERIMENTAL)
ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS = (42 | ENVIRONMENT_EXPERIMENTAL)
ENVIRONMENT_SET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE = (43 | ENVIRONMENT_EXPERIMENTAL)
ENVIRONMENT_SET_SERIALIZATION_QUIRKS = 44

SERIALIZATION_QUIRK_INCOMPLETE = (1 << 0)
SERIALIZATION_QUIRK_MUST_INITIALIZE = (1 << 1)
SERIALIZATION_QUIRK_CORE_VARIABLE_SIZE = (1 << 2)
SERIALIZATION_QUIRK_FRONT_VARIABLE_SIZE = (1 << 3)
SERIALIZATION_QUIRK_SINGLE_SESSION = (1 << 4)
SERIALIZATION_QUIRK_ENDIAN_DEPENDENT = (1 << 5)
SERIALIZATION_QUIRK_PLATFORM_DEPENDENT = (1 << 6)

ENVIRONMENT_SET_HW_SHARED_CONTEXT = (44 | ENVIRONMENT_EXPERIMENTAL)
ENVIRONMENT_GET_VFS_INTERFACE = (45 | ENVIRONMENT_EXPERIMENTAL)
ENVIRONMENT_GET_LED_INTERFACE = (46 | ENVIRONMENT_EXPERIMENTAL)

LOG_DEBUG = 0
LOG_INFO = 1
LOG_WARN = 2
LOG_ERROR = 3

SIMD_SSE = (1 << 0)
SIMD_SSE2 = (1 << 1)
SIMD_VMX = (1 << 2)
SIMD_VMX128 = (1 << 3)
SIMD_AVX = (1 << 4)
SIMD_NEON = (1 << 5)
SIMD_SSE3 = (1 << 6)
SIMD_SSSE3 = (1 << 7)
SIMD_MMX = (1 << 8)
SIMD_MMXEXT = (1 << 9)
SIMD_SSE4 = (1 << 10)
SIMD_SSE42 = (1 << 11)
SIMD_AVX2 = (1 << 12)
SIMD_VFPU = (1 << 13)
SIMD_PS = (1 << 14)
SIMD_AES = (1 << 15)
SIMD_VFPV3 = (1 << 16)
SIMD_VFPV4 = (1 << 17)
SIMD_POPCNT = (1 << 18)
SIMD_MOVBE = (1 << 19)
SIMD_CMOV = (1 << 20)
SIMD_ASIMD = (1 << 21)

retro_global_lookup = {}
for _name, _value in vars().copy().items():
    if _name.isupper():
        _prefix, _, _suffix = _name.partition('_')
        if _prefix == 'DEVICE' and _suffix.startswith('I'):
            _midfix, _, _suffix = _suffix.partition('_')
            _prefix = '{}_{}'.format(_prefix, _midfix)
        retro_global_lookup.setdefault(_prefix, dict())
        retro_global_lookup[_prefix].setdefault(_value, []).append(_suffix)
