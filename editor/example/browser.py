import MotionPicture, sys, os

app = MotionPicture.FileListPreview()
folder = "/home/sujoy/Devel/MotionPicture/editor/src/icons"
files = os.listdir(folder)
app.show_files(folder, files)


