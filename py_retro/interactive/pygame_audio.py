import ctypes
import struct

import pygame

from ..core import EmulatedSystem

g_stereo_struct = struct.Struct('<hh')

g_signed_16bit_format = -16
g_sizeof_int16 = 2
g_stereo_channels = 2
g_audio_buffer_samples = 1024
g_audio_buffer_size = g_audio_buffer_samples * g_stereo_channels * g_sizeof_int16


class PygameAudioMixin(EmulatedSystem):
    def __init__(self, libpath, **kw):
        super().__init__(libpath, **kw)
        self.__channel = None
        self.__buffer = bytearray()

    def _set_timing(self, fps, sample_rate):
        super()._set_timing(fps, sample_rate)
        init_params = (int(sample_rate), g_signed_16bit_format, g_stereo_channels)
        if pygame.mixer.get_init() != init_params:
            pygame.mixer.quit()
        pygame.mixer.init(frequency=int(sample_rate),
                          size=g_signed_16bit_format,
                          channels=g_stereo_channels,
                          buffer=g_audio_buffer_samples)
        self.__channel = pygame.mixer.Channel(0)
        self.__channel.set_volume(0.5)
        return True

    def _audio_sample(self, left, right):
        sample = g_stereo_struct.pack(left, right)
        self.__buffer.extend(sample)
        super()._audio_sample(left, right)

    def _audio_sample_batch(self, data, frames):
        samples = ctypes.string_at(data, frames * g_sizeof_int16 * g_stereo_channels)
        self.__buffer.extend(samples)
        return super()._audio_sample_batch(data, frames)

    def run(self):
        super().run()
        if self.__channel and len(self.__buffer) >= g_audio_buffer_size*4:
            self.__channel.queue(pygame.mixer.Sound(buffer=self.__buffer))
            self.__buffer = bytearray()
