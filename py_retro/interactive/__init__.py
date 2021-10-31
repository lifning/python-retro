import pygame

from ..core import EmulatedSystem
from .pygame_video import PygameVideoMixin, PygameDisplayMixin
from .pygame_audio import PygameAudioMixin
from .pygame_input import PygameJoystickMixin


class PygameFpsLimitMixin(EmulatedSystem):
    """ This mixin uses pygame.time.Clock.tick to limit the effective framerate of the game in calls to run() according
    to the FPS value provided by the core in calls to `_set_timing`."""
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
    # FIXME: PygameAudioMixin is unstable
    PygameAudioMixin,
    PygameDisplayMixin,
    PygameJoystickMixin,
):
    """ This mixin simply combines the Display, Joystick, FpsLimit, and Audio mixins to provide a minimally-functional,
    bare-bones interactive emulator."""
    pass
