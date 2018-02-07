from . import core

# implemented in terms of cpython's included batteries
from . import game_info_reader

from . import wave_audio
from . import simple_input
from . import bsv_input

# things with external dependencies that some consumers may not have or need
try:
    from . import pygame_video
    from . import pygame_audio
    from . import pygame_input
except ImportError:
    print('py_retro: pygame not available.', file=__import__('sys').stderr)

try:
    from . import portaudio_audio
except ImportError:
    print('py_retro: portaudio (pyaudio) not available.', file=__import__('sys').stderr)

from .retro_globals import *

