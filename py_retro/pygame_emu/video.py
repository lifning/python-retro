import ctypes
import pygame

from ..retro_constants import \
    PIXEL_FORMAT_0RGB1555, PIXEL_FORMAT_XRGB8888, PIXEL_FORMAT_RGB565, rcl
from ..core import EmulatedSystem


class PygameVideoMixin(EmulatedSystem):
    def __init__(self, libpath, **kw):
        self._set_pixel_format(PIXEL_FORMAT_0RGB1555)
        super().__init__(libpath, **kw)
        self.__window = None
        self.__convert = None
        self.surface = None

    def _set_pixel_format(self, fmt):
        self._pix_fmt = fmt
        if fmt == PIXEL_FORMAT_0RGB1555:
            self._bits_per_pixel = 15
            self._bit_masks = (0b0111110000000000,
                               0b0000001111100000,
                               0b0000000000011111, 0)
        elif fmt == PIXEL_FORMAT_RGB565:
            self._bits_per_pixel = 16
            self._bit_masks = (0b1111100000000000,
                               0b0000011111100000,
                               0b0000000000011111, 0)
        elif fmt == PIXEL_FORMAT_XRGB8888:
            self._bits_per_pixel = 32
            self._bit_masks = (0xff0000,
                               0x00ff00,
                               0x0000ff, 0)
        else:
            print(f'Unsupported pixel format {rcl("PIXEL", fmt)}')
            return False
        # i.e. results in a surface width of "pitch//((15+7)//8)" = "pitch//2" for 15-bit
        self._bytes_per_pixel = (self._bits_per_pixel + 7) // 8
        return super()._set_pixel_format(fmt)

    def _set_geometry(self, base_size, max_size, aspect_ratio):
        self.__window = pygame.display.set_mode(base_size)
        return super()._set_geometry(base_size, max_size, aspect_ratio)

    def _video_refresh(self, data, width, height, pitch):
        if data is not None:
            conv_width = pitch // self._bytes_per_pixel
            if (self.__convert is None
                    or self.__convert.get_width() != conv_width
                    or self.__convert.get_height() < height
                    or self.__convert.get_masks() != self._bit_masks):
                self.__convert = pygame.Surface((conv_width, height),
                                                depth=self._bits_per_pixel,
                                                masks=self._bit_masks)
                self.surface = self.__convert.subsurface((0, 0, width, height))
            elif width != self.surface.get_width() or height != self.surface.get_height():
                self.surface = self.__convert.subsurface((0, 0, width, height))
            # noinspection PyProtectedMember
            ctypes.memmove(self.__convert._pixels_address, data, pitch*height)
        super()._video_refresh(data, width, height, pitch)

    def run(self):
        super().run()
        if self.__window and self.surface:
            if self.surface.get_size() != self.__window.get_size():
                if self.surface.get_masks() == self.__window.get_masks():
                    pygame.transform.scale(self.surface, self.__window.get_size(), self.__window)
                else:
                    self.__window.blit(
                        pygame.transform.scale(self.surface, self.__window.get_size()), (0, 0))
            else:
                self.__window.blit(self.surface, (0, 0))
            pygame.display.flip()
