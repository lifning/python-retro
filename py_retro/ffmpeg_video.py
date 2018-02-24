"""
WAV-file output for libretro Audio.
"""

import subprocess
import pygame

from .pygame_emu.video import PygameVideoMixin


# Believe it or not, Pygame is a more competent image library than PIL,
# at least when it comes to converting between pixel formats
class FfmpegVideoMixin(PygameVideoMixin):
    def __init__(self, libpath, **_):
        super().__init__(libpath, **_)
        pygame.display.init()
        self.__framebuffer = None
        self.__bits_per_pixel = None
        self.__bit_masks = None
        self.__fps = None
        self.__pipe = None

    def open_video_file(self, output_file, extra_params=()):
        w, h = self.__framebuffer.get_size()
        fps = self.__fps
        cmd = [
            'ffmpeg', '-y',
            '-f', 'rawvideo',
            '-c:v', 'rawvideo',
            '-s', f'{w}x{h}',
            '-pix_fmt', 'rgb24',
            '-r', f'{fps}',
            '-i', '-',
            '-an',
            '-pix_fmt', 'yuv420p'
        ]
        cmd.extend(extra_params)
        cmd.append(output_file)
        self.__pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        return self.__pipe

    def _set_geometry(self, base_size: tuple, max_size: tuple, aspect_ratio: float) -> bool:
        if not self.__pipe:
            self.__framebuffer = pygame.Surface(
                base_size, depth=24, masks=(0x0000ff, 0x00ff00, 0xff0000, 0))
            return super()._set_geometry(base_size, max_size, aspect_ratio)
        else:
            print(f'NOT resizing to {base_size} in the middle of encoding!')
            return False

    def _set_timing(self, fps: float, sample_rate: float) -> bool:
        if not self.__pipe:
            self.__fps = fps
            return super()._set_timing(fps, sample_rate)
        else:
            print(f'NOT changing to {fps} FPS in the middle of encoding!')
            return False

    def run(self):
        super().run()
        if self.surface:
            self.__framebuffer.blit(
                pygame.transform.scale(self.surface, self.__framebuffer.get_size()),
                (0, 0)
            )
            self.__pipe.stdin.write(self.__framebuffer.get_view('2').raw)
