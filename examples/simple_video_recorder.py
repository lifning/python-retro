#!/usr/bin/env python3.6
import sys
import tempfile
import os

print(__file__)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from py_retro.recording import AVRecorderSystem

libpath, rompath = sys.argv[1:3]


def main():
    emu = AVRecorderSystem(libpath)
    emu.load_game(path=rompath)

    output_file = os.path.join(tempfile.gettempdir(), 'output.webm')

    with emu.av_record(output_file,
                       '-c:v libvpx-vp9 -qmin 0 -qmax 0 -lossless 1'.split()):
        # run for about 2 minutes
        for i in range(2*60*60):
            emu.run()


if __name__ == "__main__":
    main()
