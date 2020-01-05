from gi.repository import Gtk
from ..audio_tools import *
from ..commons import *
from ..gui_utils import ArrayViewer, FileOp, MeterBar
from moviepy.audio.AudioClip import AudioArrayClip
from moviepy.editor import AudioFileClip
import time, os, threading, numpy

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
            audio_player = self.editor.audio_player
            audio_fft = audio_player.audio_fft
            if audio_fft and self.editor.original_audio_raw_segment:
                t = audio_player.last_t % self.editor.original_audio_raw_segment.get_duration()
                self.editor.fft_viewer.set_samples(audio_fft)
                t += self.editor.playing_segment_start_time
                self.editor.play_time_entry.set_text("{0:.02f}".format(t))
                #self.editor.wave_viewer.set_playhead(t)
            time.sleep(.1)

class FreqBandSlider(Gtk.HBox):
    def __init__(self, audio_player, freq_band, split_callback,
                       min_value=0, max_value=2.0):
        Gtk.HBox.__init__(self)
        self.audio_player = audio_player
        self.freq_band = freq_band
        self.split_callback = split_callback

        self.hscale = Gtk.Scale(orientation=0)
        self.hscale.props.draw_value = False
        self.hscale.set_range(min_value, max_value)
        self.hscale.connect("value-changed", self.hscale_value_changed)

        self.entry = Gtk.SpinButton.new_with_range(min_value, max_value, 200)
        self.entry.set_digits(3)
        self.entry.connect("value-changed", self.entry_value_changed)

        self.split_button = Gtk.Button("Split")
        self.split_button.connect("clicked", self.split_button_clicked)

        self.pack_start(self.hscale, expand=True, fill=True, padding=0)
        self.pack_start(self.entry, expand=False, fill=False, padding=0)
        self.pack_start(self.split_button, expand=False, fill=False, padding=0)

        self.show_value()

    def split_button_clicked(self, widget):
        self.split_callback(self.freq_band)

    def show_value(self):
        self.hscale.set_value(self.freq_band.mult)
        self.entry.set_value(self.freq_band.mult)

    def write_to_freqband(self):
        self.freq_band.mult = self.hscale.get_value()
        self.audio_player.clear_queue()

    def hscale_value_changed(self, widget):
        self.entry.set_value(self.hscale.get_value())
        self.write_to_freqband()

    def entry_value_changed(self, widget):
        self.hscale.set_value(self.entry.get_value())
        self.write_to_freqband()

class FreqBandSliderGroup(Gtk.VBox):
    def __init__(self, audio_player, start_freq, end_freq, steps):
        Gtk.VBox.__init__(self)
        self.audio_player = audio_player
        freq_step = (end_freq-start_freq)*1.0/steps
        for i in range(steps):
            sf = start_freq + i*freq_step
            ef = start_freq + (i+1)*freq_step
            freq_band = FreqBand(sf, ef, 1.0)
            self.audio_player.freq_bands.append(freq_band)
        self.build_sliders()

    def build_sliders(self):
        for freq_band in self.audio_player.freq_bands:
            slider = FreqBandSlider(self.audio_player, freq_band, self.split_occured)

            hbox = Gtk.HBox()
            label = Gtk.Label("")
            label.set_text("{0:06d}-{1:06d}".format(
                int(freq_band.start_freq), int(freq_band.end_freq)))

            hbox.pack_start(label, expand=False, fill=False, padding=0)
            hbox.pack_start(slider, expand=True, fill=True, padding=0)

            self.pack_start(hbox, expand=False, fill=False, padding=0)
        self.show_all()

    def split_occured(self, freq_band):
        index = self.audio_player.freq_bands.index(freq_band)
        mid_freq = (freq_band.start_freq + freq_band.end_freq)*.5

        new_freq_band = FreqBand(mid_freq, freq_band.end_freq, freq_band.mult)
        freq_band.end_freq =mid_freq
        self.audio_player.freq_bands.insert(index+1, new_freq_band)

        for child in self.get_children():
            self.remove(child)

        self.build_sliders()

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

        self.topmost_box = Gtk.HBox()
        self.add(self.topmost_box)

        self.root_box = Gtk.VBox()
        self.topmost_box.pack_start(self.root_box, expand=True,  fill=True, padding=0)

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

        self.play_control_box = Gtk.HBox()
        self.root_box.pack_start(self.play_control_box, expand=False,  fill=False, padding=0)
        self.play_control_box.set_size_request(100, -1)

        self.play_start_original_button = Gtk.Button("Play Original")
        self.play_start_original_button.connect("clicked", self.play_original_button_clicked, "start")
        self.play_stop_original_button = Gtk.Button("Stop Original")
        self.play_stop_original_button.connect("clicked", self.play_original_button_clicked, "stop")

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

        self.play_time_entry = Gtk.Entry()
        self.play_time_entry.set_editable(False)

        self.play_control_box.pack_start(
                self.play_start_original_button, expand=False,  fill=False, padding=0)
        self.play_control_box.pack_start(
                self.play_stop_original_button, expand=False,  fill=False, padding=0)

        self.play_control_box.pack_start(self.reload_button, expand=False,  fill=False, padding=5)
        self.play_control_box.pack_start(self.fft_button, expand=False,  fill=False, padding=0)

        self.play_control_box.pack_start(
                self.play_start_inverse_fft_button, expand=False,  fill=False, padding=5)
        self.play_control_box.pack_start(
                self.play_stop_inverse_fft_button, expand=False,  fill=False, padding=0)

        self.play_control_box.pack_start(
                self.apply_inverse_fft_button, expand=False,  fill=False, padding=0)
        self.play_control_box.pack_start(
                self.play_time_entry, expand=False,  fill=False, padding=0)


        self.play_control_box.show_all()
        self.play_stop_original_button.hide()
        self.play_stop_inverse_fft_button.hide()

        self.record_box = Gtk.HBox()
        self.root_box.pack_start(self.record_box, expand=False,  fill=False, padding=0)

        #Recording
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

        self.record_box.pack_end(self.record_stop_button, expand=False,  fill=False, padding=0)
        self.record_box.pack_end(self.record_pause_button, expand=False,  fill=False, padding=0)
        self.record_box.pack_end(self.record_start_button, expand=False,  fill=False, padding=5)
        self.record_box.pack_end(self.record_meter, expand=False,  fill=False, padding=0)
        self.record_box.pack_end(self.record_filename_entry, expand=False,  fill=False, padding=0)

        self.record_box.show_all()
        self.record_pause_button.hide()

        #FFT View
        self.fft_label = Gtk.Label("FFT Analysis")
        self.root_box.pack_start(self.fft_label, expand=False,  fill=False, padding=0)
        self.fft_viewer = ArrayViewer(self.keyboard)
        self.root_box.pack_start(
            self.fft_viewer.get_container_box(), expand=True,  fill=True, padding=0)

        self.fft_label.show_all()
        self.fft_viewer.get_container_box().show_all()

        self.audio_player = AudioPlayer(10)
        self.audio_player.store_fft = True
        AudioJack.get_thread().create_temp_record_file()
        self.audio_player.start()


        """
        self.slider_scrolled_window = Gtk.ScrolledWindow()
        self.slider_container_box = FreqBandSliderGroup(self.audio_player, 20, 20000, 3)
        self.slider_scrolled_window.add_with_viewport(self.slider_container_box)
        self.topmost_box.pack_start(self.slider_scrolled_window, expand=True,  fill=True, padding=10)
        self.slider_scrolled_window.show()
        """
        self.freq_band_scrolled_window = Gtk.ScrolledWindow()
        self.freq_band_editor = Gtk.TextView()
        self.freq_band_scrolled_window.add_with_viewport(self.freq_band_editor)
        self.freq_band_scrolled_window.set_size_request(-1, 100)
        self.root_box.pack_start(self.freq_band_scrolled_window , expand=True,  fill=True, padding=10)
        self.freq_band_scrolled_window.show_all()

        self.freq_control_box = Gtk.HBox()
        self.root_box.pack_start(self.freq_control_box, expand=False,  fill=False, padding=0)

        for button_name in ["Player", "FFT", "Wave"]:
            apply_freq_bands_button = Gtk.Button("Apply Freq Bands in " + button_name)
            apply_freq_bands_button.connect("clicked", self.apply_freq_bands_button_clicked, button_name)
            self.freq_control_box.pack_end(apply_freq_bands_button, expand=False,  fill=False, padding=0)


        self.freq_control_box.show_all()

        self.filename = filename
        self.audio_samples = None
        self.load_audio_samples(filename)

        self.record_filename = None
        self.original_audio_raw_segment = None
        self.playing_segment_start_time = 0.
        self.inverse_fft_raw_segment = None
        self.ffted_audio_selection = None
        self.fft_samples = None
        self.record_clock = TimerClock()

        self.root_box.show()
        self.topmost_box.show()
        self.show()
        self.record_stop_button.hide()

        self.updater = UpdaterThread(self)
        self.updater.start()

    def set_freq_band_code_text(self, text):
        self.freq_band_editor.get_buffer().set_text(text)

    def apply_freq_bands_button_clicked(self, widget, apply_in):
        tbuffer = self.freq_band_editor.get_buffer()
        text = tbuffer.get_text(tbuffer.get_start_iter(), tbuffer.get_end_iter(), False)
        text = text.strip()
        if not text:
            return
        bands = eval(text)
        if isinstance(bands, list):
            if apply_in == "Player":
                del self.audio_player.freq_bands[:]
                self.audio_player.freq_bands.extend(bands)
                self.audio_player.clear_queue()
            elif apply_in == "FFT"and self.fft_samples:
                self.fft_samples.apply_freq_bands(bands)
                self.fft_viewer.redraw()
            elif apply_in == "Wave" and self.audio_samples:
                buffer_size = self.audio_player.buffer_size
                orig_samples = self.audio_samples.samples
                new_samples = None
                for si in range(0, orig_samples.shape[1], buffer_size):
                    segment_size = min(buffer_size, orig_samples.shape[1]-si)
                    segment_samples = orig_samples[:, si:si+segment_size]
                    fft_analyser = AudioFFT(segment_samples, self.audio_samples.sample_rate)
                    segment_samples = None
                    fft_analyser.apply_freq_bands(bands)
                    constructed_samples = fft_analyser.get_reconstructed_samples()
                    if new_samples is None:
                        new_samples = constructed_samples
                    else:
                        new_samples = numpy.concatenate((new_samples, constructed_samples), axis=1)
                    constructed_samples = None
                    fft_analyser = None
                self.audio_samples.set_samples(new_samples)
                self.wave_viewer.redraw()

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
            self.wave_viewer.get_selected_samples(padded=False),
            self.audio_samples.sample_rate)
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
        if not self.audio_samples:
            return
        if self.original_audio_raw_segment:
            self.audio_player.remove_segment(self.original_audio_raw_segment)
            self.original_audio_raw_segment = None
        self.audio_player.clear_queue()
        if mode == "start":
            samples = self.wave_viewer.get_selected_samples()
            self.original_audio_raw_segment = AudioRawSamples(samples, self.audio_samples.sample_rate)

            self.playing_segment_start_time = self.wave_viewer.get_selection()[0]

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
        if event.string == "a":
            self.wave_viewer.selection_width = self.audio_player.buffer_time
        elif event.string == "s":
            self.wave_viewer.selection_width = None
        elif event.string == "d":
            full_fft = AudioFFT(self.audio_samples.samples, self.audio_samples.sample_rate)
            full_fft.fft_values = full_fft.fft_values - self.fft_samples.fft_values
            self.audio_samples.set_samples(full_fft.get_reconstructed_samples())
            self.wave_viewer.redraw()
        elif event.string == "f":
            buffer_size = self.audio_player.buffer_size
            buffer_size = self.fft_samples.get_reconstructed_samples().shape[1]
            orig_samples = self.audio_samples.samples
            new_samples = None
            for si in range(0, orig_samples.shape[1], buffer_size):
                segment_size = min(buffer_size, orig_samples.shape[1]-si)
                segment_samples = orig_samples[:, si:si+segment_size]
                if segment_size<buffer_size:
                    segment_samples  = numpy.concatenate(
                        (segment_samples,
                        numpy.zeros((orig_samples.shape[0], buffer_size-segment_size), dtype="f")),
                        axis=1
                    )
                fft_analyser = AudioFFT(segment_samples, self.audio_samples.sample_rate)

                fft_analyser.fft_values = fft_analyser.fft_values - self.fft_samples.fft_values
                constructed_samples = fft_analyser.get_reconstructed_samples()
                if new_samples is None:
                    new_samples = constructed_samples
                else:
                    new_samples = numpy.concatenate((new_samples, constructed_samples), axis=1)
                constructed_samples = None
                fft_analyser = None
            new_samples = new_samples[:, :orig_samples.shape[1]]
            orig_samples = None
            self.audio_samples.set_samples(new_samples)
            self.wave_viewer.redraw()

    def quit(self, widget, event):
        if self.updater:
            self.updater.should_stop = True
            if self.updater.is_alive():
                self.updater.join()

        self.audio_player.close()
        self.audio_player = None
        if self.quit_callback:
            self.quit_callback()
