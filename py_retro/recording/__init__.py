import os
import subprocess
import tempfile
from contextlib import contextmanager

from .ffmpeg_video import FfmpegVideoMixin
from .wave_audio import WavFileAudioMixin


class AVRecorderSystem(FfmpegVideoMixin, WavFileAudioMixin):
    @contextmanager
    def av_record(self, output_file, video_params):
        temp_name = tempfile.mktemp()
        temp_vid = f'{temp_name}.webm'
        temp_aud = f'{temp_name}.wav'
        with self.video_record(temp_vid, video_params):
            with self.wav_record(temp_aud):
                yield
        subprocess.check_call(
            f'ffmpeg -y -i {temp_vid} -i {temp_aud} -c:v copy {output_file}',
            shell=True
        )
        os.unlink(temp_vid)
        os.unlink(temp_aud)
