from .retro_ctypes import *

# workarounds

HACK_need_audio_sample_batch = ['FCEUmm', 'Gambatte', 'Genesis Plus GX', 'SNES9x', 'VBA Next']
HACK_need_audio_sample = ['bNES', 'bSNES', 'Meteor GBA']

# constants

DEVICE_MASK = 0xff

DEVICE_NONE = 0
DEVICE_JOYPAD = 1
DEVICE_MOUSE = 2
DEVICE_KEYBOARD = 3
DEVICE_LIGHTGUN = 4
DEVICE_ANALOG = 5

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
DEVICE_ID_ANALOG_X = 0
DEVICE_ID_ANALOG_Y = 1

DEVICE_ID_MOUSE_X = 0
DEVICE_ID_MOUSE_Y = 1
DEVICE_ID_MOUSE_LEFT = 2
DEVICE_ID_MOUSE_RIGHT = 3

DEVICE_ID_LIGHTGUN_X = 0
DEVICE_ID_LIGHTGUN_Y = 1
DEVICE_ID_LIGHTGUN_TRIGGER = 2
DEVICE_ID_LIGHTGUN_CURSOR = 3
DEVICE_ID_LIGHTGUN_TURBO = 4
DEVICE_ID_LIGHTGUN_PAUSE = 5
DEVICE_ID_LIGHTGUN_START = 6

REGION_NTSC = 0
REGION_PAL = 1

MEMORY_MASK = 0xff
MEMORY_SAVE_RAM = 0
MEMORY_RTC = 1
MEMORY_SYSTEM_RAM = 2
MEMORY_WRAM = 2  # backwards compat
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
ENVIRONMENT_SET_GEOMETRY = 37
ENVIRONMENT_GET_USERNAME = 38
ENVIRONMENT_GET_LANGUAGE = 39
ENVIRONMENT_GET_CURRENT_SOFTWARE_FRAMEBUFFER = (40 | ENVIRONMENT_EXPERIMENTAL)
ENVIRONMENT_GET_HW_RENDER_INTERFACE = (41 | ENVIRONMENT_EXPERIMENTAL)
ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS = (42 | ENVIRONMENT_EXPERIMENTAL)
ENVIRONMENT_SET_HW_SHARED_CONTEXT = (44 | ENVIRONMENT_EXPERIMENTAL)
ENVIRONMENT_GET_VFS_INTERFACE = (45 | ENVIRONMENT_EXPERIMENTAL)

PIXEL_FORMAT_0RGB1555 = 0
PIXEL_FORMAT_XRGB8888 = 1
PIXEL_FORMAT_RGB565 = 2
MEMDESC_CONST = (1 << 0)
MEMDESC_BIGENDIAN = (1 << 1)
MEMDESC_ALIGN_2 = (1 << 16)
MEMDESC_ALIGN_4 = (2 << 16)
MEMDESC_ALIGN_8 = (3 << 16)
MEMDESC_MINSIZE_2 = (1 << 24)
MEMDESC_MINSIZE_4 = (2 << 24)
MEMDESC_MINSIZE_8 = (3 << 24)

# backwards compat:
PORT_1 = 0
PORT_2 = 1


retro_global_lookup = {}
for name, value in vars().copy().items():
    if name.isupper():
        prefix, _, suffix = name.partition('_')
        if prefix == 'DEVICE' and suffix.startswith('I'):
            midfix, _, suffix = suffix.partition('_')
            prefix = '{}_{}'.format(prefix, midfix)
        retro_global_lookup.setdefault(prefix, dict())
        retro_global_lookup[prefix][value] = suffix
        if prefix == 'ENVIRONMENT' and value & ENVIRONMENT_EXPERIMENTAL:
            retro_global_lookup[prefix][value & ~ENVIRONMENT_EXPERIMENTAL] = suffix
