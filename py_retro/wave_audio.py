"""
WAV-file output for libretro Audio.
"""

import wave
import ctypes
import struct

from .retro_globals import HACK_need_audio_sample


def set_audio_sink(core, wav_file):
    """
    Records audio to the given .wav file.

    "core" should be an instance of core.EmulatedSystem.

    "wav_file" should be either a string representing the filename
    where audio data should be written, or a file-handle opened in "wb" mode.

    Audio data will be written to the given file as a 16-bit stereo
    .wav file, using the 'wave' module from the Python standard library.

    Returns the wave.Wave_write instance used to write the audio.

    .writeframesraw() is used to append to the file.
    You *must* call .close() on the resulting instance.
    """
    res = wave.open(wav_file, 'wb')
    res.setnchannels(2)
    res.setsampwidth(2)
    res.setframerate(core.get_av_info()['sample_rate'] or 32040)
    res.setcomptype('NONE', 'not compressed')

    if HACK_need_audio_sample(core.name):
        sample = struct.Struct('<hh')
        print('set sample')
        def wrapper(left, right):
            res.writeframesraw(sample.pack(left, right))

        core.set_audio_sample_cb(wrapper)
    else:
        def wrapper(data, frames):
            size = frames * res.getnchannels() * res.getsampwidth()
            res.writeframesraw(ctypes.string_at(data, size)[:size])
            return frames
        print ('batched')
        core.set_audio_sample_batch_cb(wrapper)

    return res
