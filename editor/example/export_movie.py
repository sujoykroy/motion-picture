import MotionPicture, sys, os, subprocess

doc_filename = "/home/sujoy/Pictures/MotionPictureFiles/man.xml"
movie_filename = "/home/sujoy/Pictures/MotionPictureFiles/man.webm"
time_line = None
camera = "cam3"

doc = MotionPicture.Document(filename=doc_filename)
if doc:
    doc.make_movie(
        movie_filename, time_line=time_line, camera=camera,
        codec=None, audio=True)


#subprocess.call(["vlc", movie_filename])
