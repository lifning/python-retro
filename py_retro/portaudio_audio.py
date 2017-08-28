"""
PortAudio output for SNES Audio.
"""

import pyaudio
import ctypes
import struct
import time

from .retro_globals import HACK_need_audio_sample_batch

g_pyaudio = None
g_stream = None

g_sndlog = ''
g_consumed = 0


def consume(in_data, frame_count, time_info, status):
    global g_sndlog, g_consumed
    size = frame_count * 2 * 2
    while len(g_sndlog) < g_consumed + size:
        time.sleep(0.01)
    data = g_sndlog[g_consumed:g_consumed+size]
    g_consumed += size
    if g_consumed > 2**23:
        g_consumed = 0
        g_sndlog = ''
    return data, pyaudio.paContinue


def pyaudio_init(core):
    global g_pyaudio, g_stream
    if g_pyaudio is None:
        freq = int(core.get_av_info()['sample_rate']) or 32040
        g_pyaudio = pyaudio.PyAudio()
        g_stream = g_pyaudio.open(format=pyaudio.paInt16, channels=2, rate=freq, output=True, stream_callback=consume)
        g_stream.start_stream()


def set_audio_sample_cb(core):
    pyaudio_init(core)
    sndstruct = struct.Struct('<hh')

    def wrapper(left, right):
        global g_sndlog
        g_sndlog += sndstruct.pack(left, right)

    core.set_audio_sample_cb(wrapper)


def set_audio_sample_batch_cb(core):
    pyaudio_init(core)

    def wrapper(data, frames):
        global g_stream, g_sndlog
        g_sndlog += ctypes.string_at(data, frames*2)
        return frames

    core.set_audio_sample_batch_cb(wrapper)


def set_audio_sample_internal(core):
    if core.name in HACK_need_audio_sample_batch:
        set_audio_sample_batch_cb(core)
    else:
        set_audio_sample_cb(core)
