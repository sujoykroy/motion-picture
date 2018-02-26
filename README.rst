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

Executable building
======================
In order make executable in Windows run,
* cd <install-dir>
* python setup.py py2exe

In order make executable in Windows run,
* cd <install-dir>
* python setup.py py2app

To make sure py2app/py2exe is properly installed, run,
* cd <install-dir>
* python setup.py --help-commands

This should list py2app and py2exe as available commands.
