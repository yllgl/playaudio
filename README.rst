**Note:** This repository forks `simpleaudio <https://github.com/hamiltron/py-simple-audio/>`_. The original simpleaudio repository can only play .wav file, so I use ffmpeg that could play all kinds of audio files.

playaudio Package
===================

The playaudio package provides cross-platform audio playback
capability using ffmpeg for Python 3 on OSX, Windows, and Linux.


Installation
------------

Download this repository and reach the directory, run ::

   python setup.py build
   python setup.py install

Important! Install FFmpeg
--------------
**on Windows**: download `ffmpeg <https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z>`_ and add ffmpeg.exe path to environment variables.

**on MacOS**::

   brew install ffmpeg

**on Ubuntu**:: 

   sudo apt install ffmpeg
**run this code to check if you have install ffmpeg successfully.**::

   ffmpeg -version


Simple Example
--------------

.. code-block:: python

   import playaudio as sa

   wave_obj = sa.WaveObject.from_wave_file("path/to/file.wav")
   play_obj = wave_obj.play()
   play_obj.wait_done()


Big Thanks To ...
-----------------

Jonas Kalderstam

Christophe Gohlke

Tom Christie

Many others for their contributions, documentation, examples, and more.
