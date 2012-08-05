#!/usr/bin/python2
import pygame

import py_retro as retro
pgvid = retro.pygame_video
pgaud = retro.pygame_audio
pginp = retro.pygame_input

from sys import argv
libpath, rompath = argv[1:3]

def printrepr(arg):
	print repr(arg)

def main():
	es = retro.core.EmulatedSystem(libpath)
	es.load_game_normal(path=rompath)

	screen = pgvid.pygame_display_set_mode(es, False)
	pgaud.pygame_mixer_init(es)

	pgvid.set_video_refresh_surface(es, screen)
	pgaud.set_audio_sample_internal(es)
	pginp.set_input_poll_joystick(es)

	# run each frame until closed.
	running = True
	fps = es.get_av_info()['fps'] or 60
	clock = pygame.time.Clock()

	while running:
		es.run()
		pygame.display.flip()
		clock.tick(fps)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

if __name__ == "__main__":
	main()

