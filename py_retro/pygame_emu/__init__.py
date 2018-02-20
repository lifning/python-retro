import pygame

from ..portaudio_audio import PortaudioMixin
from .video import PygameVideoMixin
from .audio import PygameAudioMixin
from .input import PygameJoystickMixin

from ..core import EmulatedSystem


class PygameSystem(
    PortaudioMixin,  # PygameAudioMixin is crashy
    PygameVideoMixin,
    PygameJoystickMixin,
    EmulatedSystem
):
    def __init__(self, libpath, **kw):
        kw['trace'] = True
        super().__init__(libpath, **kw)
        self.__clock = pygame.time.Clock()
        self._fps = 60

    def _set_timing(self, fps, sample_rate):
        super()._set_timing(fps, sample_rate)
        self._fps = fps
        return True

    def run(self):
        super().run()
        self.__clock.tick(self._fps)
