import pyaudio
import ctypes
import struct

from ..core import EmulatedSystem, TraceStubMixin

g_stereo_struct = struct.Struct('<hh')

g_sizeof_int16 = 2
g_stereo_channels = 2


class PortaudioMixin(EmulatedSystem):
    """ This mixin plays audio provided by the core using the PyAudio bindings to the PortAudio library.
    """
    def __init__(self, libpath, **kw):
        super().__init__(libpath, **kw)
        self.__pyaudio = pyaudio.PyAudio()
        self.__stream = None
        self.__buffer = bytearray()

    def _set_timing(self, fps, sample_rate):
        super()._set_timing(fps, sample_rate)
        self.__set_sample_rate(int(sample_rate))
        return True

    def __set_sample_rate(self, sample_rate):
        if self.__stream:
            self.__stream.close()
        self.__stream = self.__pyaudio.open(
            format=pyaudio.paInt16,
            channels=g_stereo_channels,
            rate=sample_rate,
            output=True,
            stream_callback=self.__consume)
        self.__stream.start_stream()

    def __consume(self, in_data, frame_count, time_info, status):
        size = frame_count * g_sizeof_int16 * g_stereo_channels
        data, self.__buffer = self.__buffer[:size], self.__buffer[size:]
        if len(data) < size:
            if isinstance(self, TraceStubMixin):
                print(f'portaudio underrun: {len(data)} < {size}')
            data.extend([0] * (size - len(data)))
        elif len(self.__buffer) > 2*size:
            if isinstance(self, TraceStubMixin):
                print(f'portaudio overrun: {len(self.__buffer)} > {2*size}')
            self.__buffer = self.__buffer[-size:]
        return bytes(data), pyaudio.paContinue

    def _audio_sample(self, left, right):
        sample = g_stereo_struct.pack(left, right)
        self.__buffer.extend(sample)
        super()._audio_sample(left, right)

    def _audio_sample_batch(self, data, frames):
        samples = ctypes.string_at(data, frames * g_sizeof_int16 * g_stereo_channels)
        self.__buffer.extend(samples)
        return super()._audio_sample_batch(data, frames)
