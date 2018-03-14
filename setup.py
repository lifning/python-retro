#!/usr/bin/env python3.6
from distutils.core import setup, Extension

cext = Extension('py_retro.cext', sources = ['./c_ext_src/log_wrapper.c'])

setup(name='python-retro',
      version='0w0',
      description='Python bindings to libretro.',
      packages=[
          'py_retro',
          'py_retro.api',
          'py_retro.interactive',
          'py_retro.recording',
          'py_retro.tas',
      ],
      ext_modules=[cext])
