#!/usr/bin/env python3.6
import pygame
import sys

from py_retro.interactive import PygameSystem
from py_retro.tas.til_input import TilRecorderInputMixin, TilPlayerInputMixin

lib_path, rom_path, til_path = sys.argv[1:4]

if til_path.endswith('.gz'):
    open = __import__('gzip').open


class TilSystem(TilRecorderInputMixin, TilPlayerInputMixin, PygameSystem):
    pass


emu = TilSystem(lib_path)


def run_loop():
    running = True
    while running:
        emu.run()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


def record():
    emu.load_game(path=rom_path)

    # don't record until 'exit' is clicked
    run_loop()

    with emu.til_record(open(til_path, 'wb')):
        run_loop()

    emu.unload()


def replay():
    emu.load_game(path=rom_path)

    with emu.til_playback(open(til_path, 'rb')):
        run_loop()

    emu.unload()


if __name__ == "__main__":
    record()
    replay()
