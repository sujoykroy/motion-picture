import MotionPicture, sys, os

app = MotionPicture.Application()
filename = os.path.join(os.path.dirname(__file__), "sample.xml")
exit_status = app.run([sys.argv[0], filename])
sys.exit(exit_status)
