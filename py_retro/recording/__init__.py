import os
import subprocess
import tempfile
from contextlib import contextmanager

from .ffmpeg_video import FfmpegVideoMixin
from .wave_audio import WavFileAudioMixin


class AVRecorderSystem(FfmpegVideoMixin, WavFileAudioMixin):
    @contextmanager
    def av_record(self, output_file, video_params=(), audio_params=()):
        temp_name = tempfile.mktemp()
        temp_vid = f'{temp_name}.mkv'
        temp_aud = f'{temp_name}.wav'
        with self.video_record(temp_vid, video_params):
            with self.wav_record(temp_aud):
                yield

        cmd = ['ffmpeg', '-y', '-i', temp_vid, '-i', temp_aud, '-c:v', 'copy']
        cmd.extend(audio_params)
        cmd.append(output_file)
        try:
            subprocess.check_call(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
        finally:
            os.unlink(temp_vid)
            os.unlink(temp_aud)
