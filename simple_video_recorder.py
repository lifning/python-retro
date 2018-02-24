#!/usr/bin/env python3.6
import subprocess
import sys
import tempfile

import os

from py_retro.ffmpeg_video import FfmpegVideoMixin
from py_retro.wave_audio import WavFileAudioMixin

libpath, rompath = sys.argv[1:3]


class FileRecorderSystem(FfmpegVideoMixin, WavFileAudioMixin):
    pass


def main():
    emu = FileRecorderSystem(libpath)
    emu.load_game(path=rompath)

    temp_name = tempfile.mktemp()
    temp_vid = f'{temp_name}.webm'
    temp_aud = f'{temp_name}.wav'
    output_file = os.path.join(tempfile.gettempdir(), 'output.webm')

    with emu.open_video_file(temp_vid, '-qmin 0 -qmax 0 -lossless 1'.split()):
        with emu.open_wav_file(temp_aud):
            # run for about 2 minutes
            for i in range(2*60*60):
                emu.run()

    subprocess.check_call(
        f'ffmpeg -y -i {temp_vid} -i {temp_aud} -c:v copy {output_file}',
        shell=True
    )
    os.unlink(temp_vid)
    os.unlink(temp_aud)

if __name__ == "__main__":
    main()
