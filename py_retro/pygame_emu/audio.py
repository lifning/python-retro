import ctypes
import struct

import pygame

from ..core import EmulatedSystem

g_signed_16bit_format = -16
g_sizeof_int16 = 2
g_stereo_channels = 2
g_audio_buffer_samples = 1024
g_audio_buffer_size = g_audio_buffer_samples * g_stereo_channels * g_sizeof_int16


class PyGameAudioMixin(EmulatedSystem):
    def __init__(self, libpath, **kw):
        super().__init__(libpath, **kw)
        self.__audio_channel = None
        self.__stereo_struct = struct.Struct('<hh')
        self.__audio_buffer = bytearray()

    def _set_timing(self, fps, sample_rate):
        super()._set_timing(fps, sample_rate)
        self._sample_rate = sample_rate
        if pygame.mixer.get_init() != (int(sample_rate),
                                       g_signed_16bit_format,
                                       g_stereo_channels):
            pygame.mixer.quit()
        pygame.mixer.init(frequency=int(sample_rate),
                          size=g_signed_16bit_format,
                          channels=g_stereo_channels,
                          buffer=g_audio_buffer_samples)
        self.__audio_channel = pygame.mixer.Channel(0)
        self.__audio_channel.set_volume(0.5)
        return True

    def _audio_sample(self, left, right):
        sample = self.__stereo_struct.pack(left, right)
        self.__audio_buffer.extend(sample)

    def _audio_sample_batch(self, data, frames):
        samples = ctypes.string_at(data, frames * g_sizeof_int16 * g_stereo_channels)
        self.__audio_buffer.extend(samples)
        return frames

    def run(self):
        super().run()
        if self.__audio_channel and len(self.__audio_buffer) >= g_audio_buffer_size*4:
            self.__audio_channel.queue(pygame.mixer.Sound(buffer=self.__audio_buffer))
            self.__audio_buffer = bytearray()
