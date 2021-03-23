# playaudio Python Extension
# Copyright (C) 2015, Joe Hamilton
# MIT License (see LICENSE.txt)

import playaudio._playaudio as _pa
from time import sleep
import ffmpeg
import subprocess
import sys
import os
import threading
import time
COMMANDS = ('ffmpeg', 'avconv')

if sys.platform == "win32":
    PROC_FLAGS = 0x08000000
else:
    PROC_FLAGS = 0
windows_error_mode_lock = threading.Lock()
def popen_multiple(commands, command_args, *args, **kwargs):
    """Like `subprocess.Popen`, but can try multiple commands in case
    some are not available.

    `commands` is an iterable of command names and `command_args` are
    the rest of the arguments that, when appended to the command name,
    make up the full first argument to `subprocess.Popen`. The
    other positional and keyword arguments are passed through.
    """
    for i, command in enumerate(commands):
        cmd = [command] + command_args
        try:
            return subprocess.Popen(cmd, *args, **kwargs)
        except OSError:
            if i == len(commands) - 1:
                # No more commands to try.
                raise
def read_audio(filename):
    windows = sys.platform.startswith("win")
    if windows:
        windows_error_mode_lock.acquire()
        SEM_NOGPFAULTERRORBOX = 0x0002
        import ctypes
        # We call SetErrorMode in two steps to avoid overriding
        # existing error mode.
        previous_error_mode = \
            ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)
        ctypes.windll.kernel32.SetErrorMode(
            previous_error_mode | SEM_NOGPFAULTERRORBOX
        )

    try:
        devnull = open(os.devnull)
        proc = popen_multiple(
            COMMANDS,
            ['-i', filename, '-f', 's16le', '-'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=devnull,
            creationflags=PROC_FLAGS,
        )

    except OSError:
        raise NotInstalledError()

    finally:
        # Reset previous error mode on Windows. (We can change this
        # back now because the flag was inherited by the subprocess;
        # we don't need to keep it set in the parent process.)
        if windows:
            try:
                import ctypes
                ctypes.windll.kernel32.SetErrorMode(previous_error_mode)
            finally:
                windows_error_mode_lock.release()
    data = None
    while proc.poll() is None:
        out, err = proc.communicate()
        if out:
            if data is None:
                data = out
            else:
                data += out
    return data
        
class WaveObject(object):
    def __init__(self, audio_data, num_channels=2, bytes_per_sample=2,
                 sample_rate=44100):
        self.audio_data = audio_data
        self.num_channels = num_channels
        self.bytes_per_sample = bytes_per_sample
        self.sample_rate = sample_rate
    def play(self):
        return play_buffer(self.audio_data, self.num_channels,
                           self.bytes_per_sample, self.sample_rate)

    @classmethod
    def from_wave_file(cls, wave_file):
        info = ffmpeg.probe(wave_file)
        sample_rate=int(info['streams'][0]['sample_rate'])
        channels=int(info['streams'][0]['channels'])
        wave_obj = cls(read_audio(wave_file),
               channels, 2,
               sample_rate)
        return wave_obj

    @classmethod
    def from_wave_read(cls, wave_read,data=None):
        return cls(data,
                   wave_read.channels, 2,
                   wave_read.samplerate)

    def __str__(self):
        return "Wave Object: {} channel, {} bit, {} Hz".format(
            self.num_channels, self.bytes_per_sample * 8, self.sample_rate)

class PlayObject(object):
    def __init__(self, play_id):
        self.play_id = play_id

    def stop(self):
        _pa._stop(self.play_id)

    def wait_done(self):
        while self.is_playing():
            sleep(0.05)

    def is_playing(self):
        return _pa._is_playing(self.play_id)


def stop_all():
    _pa._stop_all()


def play_buffer(audio_data, num_channels, bytes_per_sample, sample_rate):
    play_id = _pa._play_buffer(audio_data, num_channels, bytes_per_sample,
                               sample_rate)
    return PlayObject(play_id)
