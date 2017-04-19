import MotionPicture
from gi.repository import Gtk
import os

def quit():
    Gtk.main_quit()
    MotionPicture.audio_tools.AudioJack.get_thread().close()

audio_editor = MotionPicture.editors.AudioEditor(quit_callback=quit)

freq_band_filename = os.path.join(os.path.dirname(__file__), "audio_freq_bands.py")
freq_band_file = open(freq_band_filename, "r")
freq_band_text = freq_band_file.read()
freq_band_file.close()

audio_editor.set_freq_band_code_text(freq_band_text)
Gtk.main()
