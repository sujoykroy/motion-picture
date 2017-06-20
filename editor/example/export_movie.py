import sys, os, subprocess

from MotionPicture import *

doc_filename = "/home/sujoy/Devel/MotionPicture/resources/sample_blender_mp.xml"
movie_filename = "/home/sujoy/Temporary/test.webm"

"""
ffmpeg -i input_file.avi -codec:v libvpx -quality good
       -cpu-used 0 -b:v 500k -qmin 10 -qmax 42
       -maxrate 500k -bufsize 1000k
       -threads 4 -vf scale=-1:480
       -codec:a libvorbis -b:a 128k output.webm
"""

ThreeDShape.HQRender = not True#should be true in production mode
doc_movies = []

if len(sys.argv)>1:
    doc_filename = sys.argv[1]
    movie_filename = os.path.join(os.path.dirname(doc_filename),
        os.path.basename(os.path.splitext(doc_filename)[0]) + ".webm")
    time_line = None

doc_movies.extend([
    DocMovie(filename=doc_filename, start_time=8, end_time=11, camera=None, time_line=None),
    DocMovie(filename="/home/sujoy/Temporary/audio_test.xml"),
    DocMovie(filename=doc_filename, start_time=5, end_time=8, camera=None, time_line=None),
])

Document.make_movie(
    doc_movies, movie_filename,
    ffmpeg_params="-quality good -qmin 10 -qmax 42",
    codec="libvpx", audio=True, speed=2, sleep=0, dry=not True)


#subprocess.call(["vlc", movie_filename])
