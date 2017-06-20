#!/usr/bin/python

import MotionPicture, sys, os

app = MotionPicture.Application()
argv = list(sys.argv)

filename = os.path.join(os.path.dirname(__file__), "sample.xml")
#argv.append(filename)

MotionPicture.Document.load_modules(
    ("test", "/home/sujoy/Devel/MotionPicture/resources/sample_blender_mp.xml")
)
ms = MotionPicture.MultiShapeModule.get_multi_shape("test.man")
print ms
exit_status = app.run(argv)
sys.exit(exit_status)
