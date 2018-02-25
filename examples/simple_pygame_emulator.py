#!/usr/bin/env python3.6
import pygame
import sys

from py_retro.interactive import PygameSystem

libpath, rompath = sys.argv[1:3]


def main():
    emu = PygameSystem(libpath)
    emu.load_game(path=rompath)

    # run each frame until closed.
    running = True
    while running:
        emu.run()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


if __name__ == "__main__":
    main()
