#!/usr/bin/env python

"""
setup.py  to build code with cython
"""
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy # to get includes
import sys # to work around windows not having libdl

sysdeps = ["cy_retro/stdio.pxd", "cy_retro/stdlib.pxd", "cy_retro/dlfcn.pxd" ]
pgdeps = ["cy_retro/SDL.pxd", "cy_retro/pygame.pxd"]

mods = [
	Extension("cy_retro.core",
		sources = ["cy_retro/core.pyx", "cy_retro/core.pxd"] + sysdeps,
		libraries = [] if sys.platform == 'win32' else ["dl"],
		language = 'C++',
	),
	Extension("cy_retro.pygame_video",
		sources = ["cy_retro/pygame_video.pyx"] + pgdeps,
		libraries = ["SDL"],
		language = 'C++',
	),
	Extension("cy_retro.pygame_audio",
		sources = ["cy_retro/pygame_audio.pyx"] + pgdeps,
		libraries = ["SDL_mixer", "SDL"],
		language = 'C++',
	),
	Extension("cy_retro.pygame_input",
		sources = ["cy_retro/pygame_input.pyx"] + pgdeps,
		libraries = ["SDL"],
		language = 'C++',
	),
	Extension("cy_retro.simple_input",
		sources = ["cy_retro/simple_input.pyx"],
		language = 'C++',
	),
]

if __name__ == "__main__":
	setup(
		name='cy_retro',
		packages=['cy_retro'],
		cmdclass = {'build_ext': build_ext},
		ext_modules = mods,
		include_dirs = ['.', '/usr/include/SDL', numpy.get_include()],
	)

