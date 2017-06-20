import MotionPicture, sys, os, subprocess

doc_filename = "/home/sujoy/Pictures/MotionPictureFiles/test.xml"
movie_filename = "/home/sujoy/Pictures/MotionPictureFiles/test.webm"

doc_filename = "/home/sujoy/Devel/MotionPicture/resources/sample_blender_mp.xml"
movie_filename = "/home/sujoy/Temporary/test.webm"

#doc_filename = "/home/sujoy/Temporary/audio_test.xml"
#movie_filename = "/home/sujoy/Temporary/audio_test.webm"

time_line = "main"
camera = None

"""
ffmpeg -i input_file.avi -codec:v libvpx -quality good
       -cpu-used 0 -b:v 500k -qmin 10 -qmax 42
       -maxrate 500k -bufsize 1000k
       -threads 4 -vf scale=-1:480
       -codec:a libvorbis -b:a 128k output.webm
"""

if len(sys.argv)>1:
    doc_filename = sys.argv[1]
    movie_filename = os.path.join(os.path.dirname(doc_filename),
        os.path.basename(os.path.splitext(doc_filename)[0]) + ".webm")
    time_line = None
#print movie_filename

doc = MotionPicture.Document(filename=doc_filename)
MotionPicture.shapes.ThreeDShape.HQRender = not True
if doc:
    doc.make_movie(
        movie_filename, time_line=time_line, camera=camera, start_time=5, end_time=None,
        ffmpeg_params="-quality good -qmin 10 -qmax 42",
        codec="libvpx", audio=True, speed=1, sleep=0, dry=not True)


#subprocess.call(["vlc", movie_filename])
