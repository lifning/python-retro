#!/usr/bin/env python

"""
setup.py  to build code with cython
"""
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy # to get includes

mods = [
	Extension("core", ["core.pyx", "core.pxd"],
		libraries=["dl"],
		language='C++',
    ),
	Extension("pygame_video", ["pygame_video.pyx"],
		libraries=["SDL"],
		language='C++',
    ),
	Extension("pygame_audio", ["pygame_audio.pyx"],
		libraries=["SDL_mixer", "SDL"],
		language='C++',
    ),
	Extension("pygame_input", ["pygame_input.pyx"],
		libraries=["SDL"],
		language='C++',
    ),
]

if __name__ == "__main__":
	setup(
    	cmdclass = {'build_ext': build_ext},
	    ext_modules = mods,
	    include_dirs = ['.', '/usr/include/SDL', numpy.get_include()],
	)

