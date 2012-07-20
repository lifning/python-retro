#!/usr/bin/python2
import pygame
import numpy

import core as C
import pygame_video as pgvid
import pygame_audio as pgaud
import pygame_input as pginp

def printrepr(arg):
	print repr(arg)

#def main():
core = C.EmulatedSystem('/usr/lib/libretro/libretro-snes9x.so')
core.load_game_normal(path='/home/lifning/Hack/Optiness/data/smw.sfc')

screen = pgvid.pygame_display_set_mode(core, False)
pgaud.pygame_mixer_init(core)

pgvid.set_video_refresh_surface(core, screen)
pgaud.set_audio_sample_internal(core)
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

#if __name__ == "__main__": main()
