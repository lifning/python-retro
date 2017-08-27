"""
Pygame output for SNES Audio.
"""

import pygame, numpy, struct, ctypes

from retro_globals import HACK_need_audio_sample_batch

sndlog = ''


def pygame_mixer_init(core):
    if not pygame.mixer.get_init():
        freq = int(core.get_av_info()['sample_rate'] or 32040)
        pygame.mixer.init(frequency=freq, size=-16, channels=2, buffer=512)


def set_audio_sample_cb(core, callback=pygame.mixer.Sound.play):
    """
    Sets the callback that will handle updated audio samples.

    Unlike core.EmulatedSNES.set_audio_sample_cb, the callback passed to this
    function should accept only one parameter:

        "snd" is an instance of pygame.mixer.Sound containing the last 512
        samples.

    If no callback function is provided, the default implementation of
    snd.play() is used.
    """
    pygame_mixer_init(core)

    maxlog = 512 * 2 * 2  # 512 stereo samples of 16-bits each
    sndstruct = struct.Struct('<hh')

    def wrapper(left, right):
        global sndlog

        sndlog += sndstruct.pack(left, right)

        if len(sndlog) >= maxlog:
            sndarr = numpy.fromstring(sndlog[:maxlog], dtype=numpy.int16).reshape((512, 2))
            callback(pygame.sndarray.make_sound(sndarr))
            sndlog = sndlog[maxlog:]

    core.set_audio_sample_cb(wrapper)


# FIXME(?) this doesn't work very well.  it sort of functions, but sounds awful.
def set_audio_sample_batch_cb(core, callback=pygame.mixer.Sound.play):
    """
    Sets the callback that will handle updated audio samples.

    Unlike core.EmulatedSNES.set_audio_sample_cb, the callback passed to this
    function should accept only one parameter:

        "snd" is an instance of pygame.mixer.Sound containing the last 512
        samples.

    If no callback function is provided, the default implementation of
    snd.play() is used.
    """
    pygame_mixer_init(core)

    def wrapper(data, frames):
        callback(pygame.mixer.Sound(buffer=ctypes.string_at(data, frames*2)))
        return frames

    core.set_audio_sample_batch_cb(wrapper)


def set_audio_sample_internal(core):
    if core.name in HACK_need_audio_sample_batch:
        set_audio_sample_batch_cb(core)
    else:
        set_audio_sample_cb(core)
