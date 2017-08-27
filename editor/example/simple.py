#!/usr/bin/python

import MotionPicture, sys, os

app = MotionPicture.Application()
argv = list(sys.argv)

#MotionPicture.Document.load_modules(("module_name", "/path/to/module"))
MotionPicture.Settings.Directory.add_new(__file__)
MotionPicture.Settings.EditingChoice.DISABLE_AUDIO = not True
exit_status = app.run(argv)
sys.exit(exit_status)
