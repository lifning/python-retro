#!/usr/bin/env python3.6
import pygame
import py_retro
import sys

lib_path, rom_path, til_path = sys.argv[1:4]

emu = py_retro.core.EmulatedSystem(lib_path)


def update_screen():
    screen = py_retro.pygame_video.pygame_display_set_mode(emu, False)
    py_retro.pygame_video.set_video_refresh_surface(emu, screen)
    return emu.get_av_info().get('fps', 60)


def run_loop(til_playback=None):
    clock = pygame.time.Clock()
    fps = update_screen()

    running = True
    while running:
        if emu.av_info_changed:
            fps = update_screen()
        if til_playback is not None and til_playback.finished:
            py_retro.pygame_input.set_input_poll_joystick(emu)
        emu.run()
        pygame.display.flip()
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


def record():
    emu.load_game_normal(path=rom_path)

    clock = pygame.time.Clock()
    fps = update_screen()

    # py_retro.portaudio_audio.set_audio_sample_internal(emu)
    py_retro.pygame_input.set_input_poll_joystick(emu)

    run_loop()

    with open(til_path, 'wb') as f:
        with py_retro.til_input.TilRecorder(emu, f):
            run_loop()

    emu.unload()


def replay():
    emu.load_game_normal(path=rom_path)

    with open(til_path, 'rb') as f:
        playback = py_retro.til_input.TilPlayer(emu, f)
        run_loop(playback)

    emu.unload()


if __name__ == "__main__":
    record()
    replay()
