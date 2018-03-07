Dependencies
=============
Check <install-dir>/requirements.txt file for required Python packages.


Usage
=========

To install the package in development mode,
open <install-dir>/scripts/install_devel.py from Thonny and run the script.

To actually run the main application,
open <install-dir>/scripts/run_simple.py from Thonny and run the script.


Tests
========

* Open system shell from Thonny.
* cd <install-dir>
* python setup.py test

Profiling
=========
To check the profile stat, run  <install-dir>/scripts/profiling.py

Building exectable on windows
==============================
* Install Nuitka from http://nuitka.net/releases/Nuitka-0.5.28.2.zip
* Extract the files from the compressed file and `cd` to that folder.
* Run following to build distribution package, assuming them img2vid source repo is
  at C:\Devel\img2vid\ directory.

  python nuitka --recurse-all C:\Devel\img2vid\scripts\run_simple.py --standalone --show-modules --python-version=3.6  --python-flag=no_site 

* It may take considerable time to build the package.
  After building the package try to run the application run_simple.exe from command line.
 `run_simple.dist\run_simple.exe`

* Most probably, you will get some error. Below some possible work arrounds are given.

* Download Visual C++ Compiler. https://www.visualstudio.com/downloads/

* Download Cython source from https://github.com/cython/cython
  and compile it, http://cython.readthedocs.io/en/latest/src/quickstart/install.html

* Download Numpy source from https://github.com/numpy/numpy/releases
  and compile using standard `python3 setup.py install`

* Download Moviepy source from https://github.com/Zulko/moviepy/releases
  and compile using standard `python3 setup.py install`

* Download ImageMagick DLL < 7.0 from ftp://ftp.imagemagick.org/pub/ImageMagick/binaries/
  Choose appropriate file. For windows 64 bit select ImageMagick-6.9.9-36-Q16-HDRI-x64-dll.exe

* Install ActiveTcl from 8.6
  - https://www.activestate.com/activetcl/downloads
  - https://www.activestate.com/activetcl/downloads/thank-you?dl=http://downloads.activestate.com/ActiveTcl/releases/8.6.6.8606/ActiveTcl-8.6.6.8606-MSWin32-x64-401995.exe

* Tweak moviepy codes,-
  - moviepy\decorator.py
    go to near bottom of page, and change compact dict making script into following snippet.

    for (k,v) in k.items():
      new_kw[k] = fun(v) if k=='fps' else v

  - audio\fx\all\__init__.py
    append following lines,
    from ..audio_fadein import audio_fadein
    from ..audio_fadeout import audio_fadeout
    from ..audio_left_right import audio_left_right
    from ..audio_loop import audio_loop
    from ..volumex import volumex

  - video\fx\all\__init__.py
    append following lines,
    from ..accel_decel import accel_decel
    from ..blackwhite import blackwhite
    from ..blink import blink
    from ..colorx import colorx
    from ..crop import crop
    from ..even_size import even_size
    from ..fadein import fadein
    from ..fadeout import fadeout
    from ..freeze import freeze
    from ..freeze_region import freeze_region
    from ..headblur import headblur
    from ..invert_colors import invert_colors
    from ..loop import loop
    from ..lum_contrast import lum_contrast
    from ..make_loopable import make_loopable
    from ..margin import margin
    from ..mask_and import mask_and
    from ..mask_color import mask_color
    from ..mask_or import mask_or
    from ..mirror_x import mirror_x
    from ..mirror_y import mirror_y
    from ..painting import painting
    from ..resize import resize
    from ..rotate import rotate
    from ..speedx import speedx
    from ..supersample import supersample
    from ..time_mirror import time_mirror
    from ..time_symmetrize import time_symmetrize

* Run scripts\build_with_nuitka.bat
  You may need to edit the file to adjust different file path.


Legacy ImageMagick binaries,
=============================================
You can download legacey ImageMagick from https://legacy.imagemagick.org/script/binary-releases.php


