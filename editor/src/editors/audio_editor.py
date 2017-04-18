from gi.repository import Gtk
from ..audio_tools import *
from ..commons import *
from ..gui_utils import ArrayViewer, FileOp, MeterBar
from moviepy.audio.AudioClip import AudioArrayClip
from moviepy.editor import AudioFileClip
import time, os, threading

class UpdaterThread(threading.Thread):
    def __init__(self, editor):
        threading.Thread.__init__(self)
        self.should_stop = False
        self.editor = editor

    def run(self):
        while not self.should_stop:
            audio_jack = AudioJack.get_thread()
            if audio_jack.record:
                self.editor.set_record_amplitude(audio_jack.record_amplitude)
            time.sleep(.1)

class AudioEditor(Gtk.Window):
    def __init__(self, filename=None, quit_callback=None, width=200, height=200):
        Gtk.Window.__init__(self)
        self.quit_callback = quit_callback
        self.keyboard = Keyboard()

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(width, height)
        self.connect("delete-event", self.quit)
        self.connect("key-press-event", self.on_drawing_area_key_press)
        self.connect("key-release-event", self.on_drawing_area_key_release)

        self.root_box = Gtk.VBox()
        self.add(self.root_box)

        self.filename_entry = Gtk.Entry()
        self.filename_entry.set_editable(False)
        self.file_open_button = Gtk.Button("Open")
        self.file_open_button.connect("clicked", self.file_open_button_clicked)
        self.file_save_as_button = Gtk.Button("Save As")
        self.file_save_as_button.connect("clicked", self.file_save_as_button_clicked)

        self.file_box = Gtk.HBox()
        self.root_box.pack_start(self.file_box, expand=False,  fill=False, padding=0)

        self.file_box.pack_start(self.filename_entry, expand=True,  fill=True, padding=0)
        self.file_box.pack_end(self.file_save_as_button, expand=False, fill=False, padding=0)
        self.file_box.pack_end(self.file_open_button, expand=False, fill=False, padding=0)
        self.file_box.show_all()

        self.wave_label = Gtk.Label("Wave")
        self.root_box.pack_start(self.wave_label, expand=False,  fill=False, padding=0)
        self.wave_viewer = ArrayViewer(self.keyboard)
        self.root_box.pack_start(
            self.wave_viewer.get_container_box(), expand=True,  fill=True, padding=0)
        self.wave_label.show_all()
        self.wave_viewer.get_container_box().show_all()

        self.control_box = Gtk.HBox()
        self.root_box.pack_start(self.control_box, expand=False,  fill=False, padding=0)
        self.control_box.set_size_request(100, -1)

        self.play_start_original_button = Gtk.Button("Play Original")
        self.play_start_original_button.connect("clicked", self.play_original_button_clicked, "start")
        self.play_stop_original_button = Gtk.Button("Stop Original")
        self.play_stop_original_button.connect("clicked", self.play_original_button_clicked, "stop")

        self.record_filename_entry = Gtk.Entry()
        self.record_filename_entry.set_editable(False)
        self.record_start_button = Gtk.Button("Record Start")
        self.record_start_button.connect("clicked", self.record_button_clicked, "start")
        self.record_pause_button = Gtk.Button("Record Pause")
        self.record_pause_button.connect("clicked", self.record_button_clicked, "pause")
        self.record_stop_button = Gtk.Button("Record Stop")
        self.record_stop_button.connect("clicked", self.record_button_clicked, "stop")
        self.record_meter = MeterBar()
        self.record_meter.set_size_request(100, -1)

        self.reload_button = Gtk.Button("Reload Original")
        self.reload_button.connect("clicked", self.reload_button_clicked)

        self.fft_button = Gtk.Button("FFT Selected")
        self.fft_button.connect("clicked", self.fft_button_clicked)

        self.play_start_inverse_fft_button = Gtk.Button("Play Inverse FFT")
        self.play_start_inverse_fft_button.connect("clicked", self.play_inverse_fft_button_clicked, "start")
        self.play_stop_inverse_fft_button = Gtk.Button("Stop Inverse FFT")
        self.play_stop_inverse_fft_button.connect("clicked", self.play_inverse_fft_button_clicked, "stop")

        self.apply_inverse_fft_button = Gtk.Button("Apply Inverse FFT")
        self.apply_inverse_fft_button.connect("clicked", self.apply_inverse_fft_button_clicked)

        self.control_box.pack_start(
                self.play_start_original_button, expand=False,  fill=False, padding=0)
        self.control_box.pack_start(
                self.play_stop_original_button, expand=False,  fill=False, padding=0)

        self.control_box.pack_end(self.record_stop_button, expand=False,  fill=False, padding=0)
        self.control_box.pack_end(self.record_pause_button, expand=False,  fill=False, padding=0)
        self.control_box.pack_end(self.record_start_button, expand=False,  fill=False, padding=5)
        self.control_box.pack_end(self.record_meter, expand=False,  fill=False, padding=0)
        self.control_box.pack_end(self.record_filename_entry, expand=False,  fill=False, padding=0)

        self.control_box.pack_start(self.reload_button, expand=False,  fill=False, padding=5)
        self.control_box.pack_start(self.fft_button, expand=False,  fill=False, padding=0)

        self.control_box.pack_start(
                self.play_start_inverse_fft_button, expand=False,  fill=False, padding=5)
        self.control_box.pack_start(
                self.play_stop_inverse_fft_button, expand=False,  fill=False, padding=0)

        self.control_box.pack_start(
                self.apply_inverse_fft_button, expand=False,  fill=False, padding=0)

        self.control_box.show_all()
        self.record_pause_button.hide()
        self.play_stop_original_button.hide()
        self.play_stop_inverse_fft_button.hide()

        self.fft_label = Gtk.Label("FFT Analysis")
        self.root_box.pack_start(self.fft_label, expand=False,  fill=False, padding=0)
        self.fft_viewer = ArrayViewer(self.keyboard)
        self.root_box.pack_start(
            self.fft_viewer.get_container_box(), expand=True,  fill=True, padding=0)

        self.fft_label.show_all()
        self.fft_viewer.get_container_box().show_all()

        self.audio_player = AudioPlayer(10)
        self.audio_player.start()
        AudioJack.get_thread().create_temp_record_file()

        self.filename = filename
        self.load_audio_samples(filename)

        self.record_filename = None
        self.original_audio_raw_segment = None
        self.inverse_fft_raw_segment = None
        self.ffted_audio_selection = None
        self.fft_samples = None
        self.record_clock = TimerClock()

        self.root_box.show()
        self.show()
        self.record_stop_button.hide()

        self.updater = UpdaterThread(self)
        self.updater.start()

    def load_audio_samples(self, filename):
        if not filename:
            return
        self.audio_samples = AudioFileSamples(filename)
        self.audio_samples.load_samples()
        self.wave_viewer.set_samples(self.audio_samples)

    def file_open_button_clicked(self, widget):
        filename = FileOp.choose_file(self, "open", file_types="audio", filename=self.filename)
        self.load_audio_samples(filename)
        if filename:
            self.set_filename(filename)

    def file_save_as_button_clicked(self, widget):
        filename = FileOp.choose_file(self, "save_as", file_types="audio", filename=self.filename)
        if filename:
            clip = AudioArrayClip(self.audio_samples.samples.T, fps=self.audio_samples.sample_rate)
            clip.write_audiofile(filename)
            self.set_filename(filename)

    def set_record_amplitude(self, amp):
        self.record_meter.set_fraction(amp)
        self.record_meter.set_text("{0} sec".format(int(self.record_clock.get_duration())))

    def set_filename(self, filename):
        self.filename = filename
        self.filename_entry.set_text(filename)

    def set_record_filename(self, filename):
        self.record_filename = filename
        self.record_filename_entry.set_text(filename)

    def fft_button_clicked(self, widget):
        selection = self.wave_viewer.get_selection()
        self.ffted_audio_selection = selection
        text = "FFT Analysis"
        if selection:
            text += "({0:.2f}-{1:.2f})".format(*selection)
        self.fft_label.set_text(text)
        self.fft_samples = AudioFFT(
            self.wave_viewer.get_selected_samples(), self.audio_samples.sample_rate)
        self.fft_viewer.set_samples(self.fft_samples)

    def apply_inverse_fft_button_clicked(self, widget):
        if self.fft_samples is None:
            return

        self.audio_samples.replace_samples(
            self.ffted_audio_selection,
            self.fft_samples.get_reconstructed_samples()
        )
        self.wave_viewer.redraw()

    def reload_button_clicked(self, widget):
        self.audio_samples.load_samples()
        self.wave_viewer.reset_dimensions(redraw=True)

    def play_inverse_fft_button_clicked(self, widget, mode):
        if self.fft_samples is None:
            return
        if self.inverse_fft_raw_segment:
            self.audio_player.remove_segment(self.inverse_fft_raw_segment)
            self.inverse_fft_raw_segment = None
        self.audio_player.clear_queue()
        if mode == "start":
            samples = self.fft_samples.get_reconstructed_samples()
            self.inverse_fft_raw_segment = AudioRawSamples(samples, self.fft_samples.sample_rate)
            self.audio_player.add_segment(self.inverse_fft_raw_segment)
            self.play_stop_inverse_fft_button.show()
            self.play_start_inverse_fft_button.hide()
        else:
            self.play_start_inverse_fft_button.show()
            self.play_stop_inverse_fft_button.hide()

    def play_original_button_clicked(self, widget, mode):
        if self.original_audio_raw_segment:
            self.audio_player.remove_segment(self.original_audio_raw_segment)
            self.original_audio_raw_segment = None
        self.audio_player.clear_queue()
        if mode == "start":
            samples = self.wave_viewer.get_selected_samples()
            self.original_audio_raw_segment = AudioRawSamples(samples, self.audio_samples.sample_rate)
            self.audio_player.add_segment(self.original_audio_raw_segment)
            self.play_stop_original_button.show()
            self.play_start_original_button.hide()
        else:
            self.play_start_original_button.show()
            self.play_stop_original_button.hide()

    def record_button_clicked(self, widget, mode):
        audio_jack = AudioJack.get_thread()
        if mode == "start":
            if self.record_filename is None:
                filename = FileOp.choose_file(self, purpose="save_as", file_types="audio")
                if filename:
                    self.set_record_filename(filename)
                    self.record_clock.reset()
            else:
                self.record_pause_button.show()
                self.record_stop_button.show()
                self.record_start_button.hide()
                audio_jack.record = True
                self.record_clock.start()
        elif mode == "pause":
            self.record_pause_button.hide()
            self.record_stop_button.show()
            self.record_start_button.show()
            audio_jack.record = False
            self.record_clock.pause()
        elif mode == "stop":
            self.record_pause_button.hide()
            self.record_start_button.show()
            self.record_stop_button.hide()
            audio_jack.record = False
            self.record_clock.pause()
            if self.record_filename:
                mid_filename = self.record_filename + ".{0}.wav".format(time.time())
                if audio_jack.save_record_file_as(mid_filename):
                    clip = AudioFileClip(mid_filename)
                    clip.write_audiofile(self.record_filename)
                    os.remove(mid_filename)
                    self.load_audio_samples(self.record_filename)
                    self.set_filename(self.record_filename)
            self.set_record_filename("")

    def on_drawing_area_key_press(self, widget, event):
        self.keyboard.set_keypress(event.keyval, pressed=True)

    def on_drawing_area_key_release(self, widget, event):
        self.keyboard.set_keypress(event.keyval, pressed=False)

    def quit(self, widget, event):
        if self.updater:
            self.updater.should_stop = True
            if self.updater.is_alive():
                self.updater.join()

        self.audio_player.close()
        self.audio_player = None
        if self.quit_callback:
            self.quit_callback()
