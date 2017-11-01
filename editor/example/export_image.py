import sys, os, subprocess
from MotionPicture import *

doc_filename = sys.argv[1]
time_line = sys.argv[2]
at = float(sys.argv[3])
image_filename = sys.argv[4]
Document.save_as_image(doc_filename, time_line, at, image_filename)

