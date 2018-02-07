#!/usr/bin/env python3.6
import pygame
import py_retro
import sys

libpath, rompath = sys.argv[1:3]


def main():
    emu = py_retro.core.EmulatedSystem(libpath)
    emu.load_game_normal(path=rompath)

    fps = emu.get_av_info().get('fps', 60)
    screen = py_retro.pygame_video.pygame_display_set_mode(emu, False)
    py_retro.pygame_video.set_video_refresh_surface(emu, screen)

    py_retro.portaudio_audio.set_audio_sample_internal(emu)
    py_retro.pygame_input.set_input_poll_joystick(emu)

    # run each frame until closed.
    running = True
    clock = pygame.time.Clock()

    while running:
        if emu.av_info_changed:
            fps = emu.get_av_info().get('fps', 60)
            screen = py_retro.pygame_video.pygame_display_set_mode(emu, False)
            py_retro.pygame_video.set_video_refresh_surface(emu, screen)
        emu.run()
        pygame.display.flip()
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


if __name__ == "__main__":
    main()
