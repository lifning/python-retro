import ctypes
import struct
import pygame

from .core import EmulatedSystem, _rgl
from .retro_globals import *

g_audio_buffer_size = 512
g_stereo_channels = 2
g_sizeof_int16 = 2

# xinput mappings because lazy
g_button_map = {
    DEVICE_ID_JOYPAD_B: lambda j: j.get_button(0),
    DEVICE_ID_JOYPAD_Y: lambda j: j.get_button(2),
    DEVICE_ID_JOYPAD_SELECT: lambda j: j.get_button(6),
    DEVICE_ID_JOYPAD_START: lambda j: j.get_button(7),
    DEVICE_ID_JOYPAD_UP: lambda j: j.get_hat(0)[1] > 0,
    DEVICE_ID_JOYPAD_DOWN: lambda j: j.get_hat(0)[1] < 0,
    DEVICE_ID_JOYPAD_LEFT: lambda j: j.get_hat(0)[0] < 0,
    DEVICE_ID_JOYPAD_RIGHT: lambda j: j.get_hat(0)[0] > 0,
    DEVICE_ID_JOYPAD_A: lambda j: j.get_button(1),
    DEVICE_ID_JOYPAD_X: lambda j: j.get_button(3),
    DEVICE_ID_JOYPAD_L: lambda j: j.get_button(4),
    DEVICE_ID_JOYPAD_R: lambda j: j.get_button(5),
    DEVICE_ID_JOYPAD_L2: lambda j: max(0, 32767 * j.get_axis(2)),
    DEVICE_ID_JOYPAD_R2: lambda j: max(0, 32767 * j.get_axis(5)),
    DEVICE_ID_JOYPAD_L3: lambda j: j.get_button(9),
    DEVICE_ID_JOYPAD_R3: lambda j: j.get_button(10),
}

g_stick_map = {
    DEVICE_INDEX_ANALOG_LEFT: {
        DEVICE_ID_ANALOG_X: lambda j: 32767 * j.get_axis(0),
        DEVICE_ID_ANALOG_Y: lambda j: 32767 * j.get_axis(1),
    },
    DEVICE_INDEX_ANALOG_RIGHT: {
        DEVICE_ID_ANALOG_X: lambda j: 32767 * j.get_axis(3),
        DEVICE_ID_ANALOG_Y: lambda j: 32767 * j.get_axis(4),
    },
}


class PyGameSystem(EmulatedSystem):
    def __init__(self, libpath):
        self._set_pixel_format(PIXEL_FORMAT_0RGB1555)
        super().__init__(libpath)
        self.__window = None
        self.__convert = None
        self.screen = None
        self.__clock = pygame.time.Clock()
        self.__audio_channel = None
        self.__stereo_struct = struct.Struct('<hh')
        self.__audio_buffer = bytearray()
        pygame.joystick.init()
        self.__joystick = pygame.joystick.Joystick(0)
        self.__joystick.init()
        self.__joy_states = dict()

    def _set_pixel_format(self, fmt):
        self._pix_fmt = fmt
        if fmt == PIXEL_FORMAT_0RGB1555:
            self._bits_per_pixel = 15
            self._bit_masks = (0b0111110000000000,
                               0b0000001111100000,
                               0b0000000000011111, 0)
        elif fmt == PIXEL_FORMAT_XRGB8888:
            self._bits_per_pixel = 32
            self._bit_masks = (0xff0000,
                               0x00ff00,
                               0x0000ff, 0)
        elif fmt == PIXEL_FORMAT_RGB565:
            self._bits_per_pixel = 16
            self._bit_masks = (0b1111100000000000,
                               0b0000011111100000,
                               0b0000000000011111, 0)
        else:
            print(f'Unsupported pixel format {_rgl("PIXEL", fmt)}')
            return False
        # i.e. results in a surface width of "pitch//((15+7)//8)" = "pitch//2" for 15-bit
        self._bytes_per_pixel = (self._bits_per_pixel + 7) // 8
        return True

    def _set_geometry(self, base_size, max_size, aspect_ratio):
        self.__window = pygame.display.set_mode(base_size)
        return True

    def _set_timing(self, fps, sample_rate):
        self._fps = fps
        self._sample_rate = sample_rate
        if not pygame.mixer.get_init():
            freq = int(sample_rate)
            pygame.mixer.init(frequency=freq,
                              size=-16,  # signed 16-bit
                              channels=g_stereo_channels,
                              buffer=g_audio_buffer_size)
            self.__audio_channel = pygame.mixer.Channel(0)
            self.__audio_channel.set_volume(0.5)
        return True

    def _video_refresh(self, data, width, height, pitch):
        if data is not None:
            conv_width = pitch // self._bytes_per_pixel
            if (self.__convert is None
                    or self.__convert.get_width() != conv_width
                    or self.__convert.get_height() < height
                    or self.__convert.get_masks() != self._bit_masks):
                self.__convert = pygame.Surface((conv_width, height),
                                                depth=self._bits_per_pixel,
                                                masks=self._bit_masks)
                self.screen = self.__convert.subsurface((0, 0, width, height))
            elif width != self.screen.get_width():
                self.screen = self.__convert.subsurface((0, 0, width, height))
            # noinspection PyProtectedMember
            ctypes.memmove(self.__convert._pixels_address, data, pitch*height)

    def _audio_sample(self, left, right):
        sample = self.__stereo_struct.pack(left, right)
        self.__audio_buffer.extend(sample)

    def _audio_sample_batch(self, data, frames):
        samples = ctypes.string_at(data, frames * g_sizeof_int16 * g_stereo_channels)
        self.__audio_buffer.extend(samples)
        return frames

    def _input_poll(self):
        port = 0
        device = DEVICE_JOYPAD
        index = 0
        for id_, fn in g_button_map.items():
            key = bytes((port, device, index, id_))
            val = int(fn(self.__joystick))
            self.__joy_states[key] = val
        device = DEVICE_ANALOG
        for index in (DEVICE_INDEX_ANALOG_LEFT, DEVICE_INDEX_ANALOG_RIGHT):
            for id_, fn in g_stick_map[index].items():
                key = bytes((port, device, index, id_))
                val = int(fn(self.__joystick))
                self.__joy_states[key] = val

    def _input_state(self, port, device, index, id_):
        key = bytes((port, device, index, id_))
        val = self.__joy_states.get(key, 0)
        return val

    def run(self):
        super().run()
        if self.__window and self.screen:
            self.__window.blit(self.screen, (0, 0))
            pygame.display.flip()
        if self.__audio_channel:
            self.__audio_channel.queue(pygame.mixer.Sound(buffer=self.__audio_buffer))
            self.__audio_buffer = bytearray()
        self.__clock.tick(self._fps)
