import sys, os, subprocess
from MotionPicture import *
import time

doc_filename = sys.argv[1]
time_line = sys.argv[2]
at = float(sys.argv[3])
image_filename = sys.argv[4]

if len(sys.argv)>5:
    w, h = sys.argv[5].split("x")
    w, h = float(w), float(h)
else:
    w, h = None, None

st = time.time()
Document.save_as_image(doc_filename, time_line, at, image_filename,w, h)
print("Proccessed in {0} seconds".format(int(time.time()-st)))

