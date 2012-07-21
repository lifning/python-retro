#!/usr/bin/python2
import pygame

import py_retro as retro
C = retro.core
pgvid = retro.pygame_video
pgaud = retro.pygame_audio
pginp = retro.pygame_input

def printrepr(arg):
	print repr(arg)

def main():
	core = C.EmulatedSystem('C:/Users/lifning/Games/retroarch-win64/libretro-git-fceu-x86_64.dll')
	core.load_game_normal(path='C:/Users/lifning/ROMs/nes/Super Mario Bros.nes')

	screen = pgvid.pygame_display_set_mode(core, False)
	pgaud.pygame_mixer_init(core)

	pgvid.set_video_refresh_surface(core, screen)
	pgaud.set_audio_sample_cb(core)
	pginp.set_input_poll_joystick(core)

	# run each frame until closed.
	running = True
	fps = core.get_av_info()['fps'] or 60
	clock = pygame.time.Clock()

	while running:
		core.run()
		pygame.display.flip()
		clock.tick(fps)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

if __name__ == "__main__":
	main()
