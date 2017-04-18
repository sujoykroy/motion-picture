import MotionPicture
from gi.repository import Gtk

def quit():
    Gtk.main_quit()
    MotionPicture.audio_tools.AudioJack.get_thread().close()

audio_editor = MotionPicture.editors.AudioEditor(quit_callback=quit)
Gtk.main()
