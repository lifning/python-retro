#!/usr/bin/env python3.6
from subprocess import SubprocessError

import pygame
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from py_retro.interactive import PygameSystem
from py_retro.recording import AVRecorderSystem
from py_retro.tas import TilRecorderInputMixin, TilPlayerInputMixin

libpath, rompath = sys.argv[1:3]


class FeaturedSystem(
    TilRecorderInputMixin,
    TilPlayerInputMixin,
    AVRecorderSystem,
    PygameSystem
):
    pass


def main():
    emu = FeaturedSystem(libpath)
    emu.load_game(path=rompath)

    # TODO: it'd be cool to support doing these simultaneously, like...
    # - recording a TIL from a subset of another TIL
    # - rendering a TIL to video
    # - making a savestate in the middle of a TIL
    # - adding checkpoint savestates while recording a TIL
    running = True
    while running:
        emu.run()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F2:
                    try:
                        with open(f'{rompath}.state', 'wb') as f:
                            f.write(emu.serialize())
                            print('saved state.')
                    except IOError:
                        print('could not write state.')
                elif event.key == pygame.K_F4:
                    try:
                        with open(f'{rompath}.state', 'rb') as f:
                            emu.unserialize(f.read())
                            print('loaded state.')
                    except IOError:
                        print('could not read state.')
                elif event.key == pygame.K_o:
                    try:
                        with emu.til_record(open(f'{rompath}.til', 'wb')):
                            print('recording til, press ESC to end...')
                            while not pygame.key.get_pressed()[pygame.K_ESCAPE]:
                                emu.run()
                                pygame.event.pump()
                            print('done recording til.')
                    except IOError:
                        print('could not write til.')
                elif event.key == pygame.K_p:
                    try:
                        with emu.til_playback(open(f'{rompath}.til', 'rb')):
                            print('playing til, press ESC to cancel...')
                            while emu.til_is_playing() and not pygame.key.get_pressed()[pygame.K_ESCAPE]:
                                emu.run()
                                pygame.event.pump()
                            print('done playing til.')
                    except IOError:
                        print('could not read til.')
                elif event.key == pygame.K_v:
                    try:
                        with emu.av_record(f'{rompath}.webm', ['-c:v', 'libvpx-vp9']):
                            print('recording video, press ESC to end...')
                            while not pygame.key.get_pressed()[pygame.K_ESCAPE]:
                                emu.run()
                                pygame.event.pump()
                            print('done recording video.')
                    except SubprocessError:
                        print('could not invoke ffmpeg.')


if __name__ == "__main__":
    main()
