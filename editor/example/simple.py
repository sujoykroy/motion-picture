#!/usr/bin/python

import MotionPicture, sys, os

app = MotionPicture.Application()
argv = list(sys.argv)

filename = os.path.join(os.path.dirname(__file__), "sample.xml")
#argv.append(filename)

exit_status = app.run(argv)
sys.exit(exit_status)
