#!/usr/bin/python

import MotionPicture, sys, os

app = MotionPicture.Application()
argv = list(sys.argv)

filename = os.path.join(os.path.dirname(__file__), "sample.xml")
#argv.append(filename)

MotionPicture.Document.load_modules(
    ("test", "/home/sujoy/Devel/MotionPicture/resources/sample_blender_mp.xml")
)
MotionPicture.Settings.Directory.add_new(__file__)
exit_status = app.run(argv)
sys.exit(exit_status)
