import sys, os, subprocess
from MotionPicture import *
from moviepy.editor import VideoFileClip

if len(sys.argv)>1:
    doc_filename = sys.argv[1]

ThreeDShape.HQRender = not True#should be true in production mode
doc_movie = DocMovie.create_from_params(doc_filename, sys.argv[2:])

ThreeDShape.HQRender = not True#should be true in production mode
#ThreeDShape.HQRender = True
kwargs = dict(
    doc_movie=doc_movie,
    wh=["160x90","320x180", "640x360", "1280x720"][1],
    audio=True, dry=not True)

Document.make_movie_faster(process_count=3, **kwargs)

clip=VideoFileClip(doc_movie.dest_filename)
print(doc_movie.dest_filename, "duration is", clip.duration)
subprocess.call(["vlc", doc_movie.dest_filename])
