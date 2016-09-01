import MotionPicture, sys, os

app = MotionPicture.Application()
argv = [sys.argv[0]]

filename = os.path.join(os.path.dirname(__file__), "sample.xml")
argv.append(filename)

exit_status = app.run(argv)
sys.exit(exit_status)
