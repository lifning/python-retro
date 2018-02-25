"""
WAV-file output for libretro Audio.
"""

import wave
import ctypes
import struct

from .core import EmulatedSystem

g_sizeof_int16 = 2
g_stereo_channels = 2
g_stereo_struct = struct.Struct('<hh')


class WavFileAudioMixin(EmulatedSystem):
    def __init__(self, libpath, **kw):
        super().__init__(libpath, **kw)
        self.__wav = None
        self.__sample_rate = None

    def wav_record(self, wav_file):
        """
        Records audio to the given .wav file.

        "wav_file" should be either a string representing the filename
        where audio data should be written, or a file-handle opened in "wb" mode.

        Audio data will be written to the given file as a 16-bit stereo
        .wav file, using the 'wave' module from the Python standard library.

        Returns the wave.Wave_write instance used to write the audio.

        .writeframesraw() is used to append to the file.
        You *must* call .close() on the resulting instance.
        """
        self.__wav = wave.open(wav_file, 'wb')
        self.__wav.setnchannels(g_stereo_channels)
        self.__wav.setsampwidth(g_sizeof_int16)
        self.__wav.setframerate(self.__sample_rate)
        self.__wav.setcomptype('NONE', 'not compressed')
        return self.__wav

    def _set_timing(self, fps, sample_rate):
        self.__sample_rate = sample_rate
        return super()._set_timing(fps, sample_rate)

    def _audio_sample(self, left, right):
        if self.__wav and self.__wav._file:
            self.__wav.writeframesraw(g_stereo_struct.pack(left, right))
        super()._audio_sample(left, right)

    def _audio_sample_batch(self, data, frames):
        if self.__wav and self.__wav._file:
            size = frames * self.__wav.getnchannels() * self.__wav.getsampwidth()
            self.__wav.writeframesraw(ctypes.string_at(data, size)[:size])
        return super()._audio_sample_batch(data, frames)
