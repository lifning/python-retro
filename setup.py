#!/usr/bin/env python

from distutils.core import setup

if __name__ == "__main__":
    setup(
        name='py_retro',
        packages=['py_retro'],
        requires=['pygame', 'pyaudio']
    )
