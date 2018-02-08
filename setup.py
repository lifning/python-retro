#!/usr/bin/env python3.6
from distutils.core import setup, Extension

cext = Extension('cext', sources = ['./c_ext_src/log_wrapper.c'])

setup(name='python-retro',
      version='0w0',
      description='Python bindings to libretro.',
      ext_modules=[cext])
