import pygame

from ..core import EmulatedSystem
from .pygame_video import PygameVideoMixin, PygameDisplayMixin
from .pygame_audio import PygameAudioMixin
from .pygame_input import PygameJoystickMixin

# PygameAudioMixin is crashy
from .portaudio_audio import PortaudioMixin


class PygameFpsLimitMixin(EmulatedSystem):
    def __init__(self, libpath, **kw):
        super().__init__(libpath, **kw)
        self.__clock = pygame.time.Clock()
        self.__fps = 60

    def _set_timing(self, fps, sample_rate):
        super()._set_timing(fps, sample_rate)
        self.__fps = fps
        return True

    def run(self):
        super().run()
        self.__clock.tick(self.__fps)


class PygameSystem(
    PygameFpsLimitMixin,
    PortaudioMixin,
    PygameDisplayMixin,
    PygameJoystickMixin,
):
    pass
