import MotionPicture, sys, os, subprocess

doc_filename = "/home/sujoy/Pictures/MotionPictureFiles/test.xml"
movie_filename = "/home/sujoy/Pictures/MotionPictureFiles/test.webm"

doc_filename = "/home/sujoy/Devel/MotionPicture/resources/sample_blender_mp.xml"
movie_filename = "/home/sujoy/Temporary/test.webm"
time_line = "main"
camera = None

doc = MotionPicture.Document(filename=doc_filename)
if doc:
    doc.make_movie(
        movie_filename, time_line=time_line, camera=camera,
        codec=None, audio=True, speed=2)


#subprocess.call(["vlc", movie_filename])
