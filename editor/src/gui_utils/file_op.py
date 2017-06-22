from gi.repository import Gtk, GObject
import Queue
from ..audio_tools import *

class FileOp(object):
    @staticmethod
    def choose_file(parent, purpose, file_types=[["Motion Picture", "text/xml"]], filename=None):
        if purpose == "save":
            title = "Save"
            action = Gtk.FileChooserAction.SAVE
            ok_key = Gtk.STOCK_SAVE
        elif purpose == "save_as":
            title = "Save As"
            action = Gtk.FileChooserAction.SAVE
            ok_key = Gtk.STOCK_SAVE_AS
        elif purpose == "open":
            title = "Open file"
            action = Gtk.FileChooserAction.OPEN
            ok_key = Gtk.STOCK_OPEN

        dialog = FileChooserDialog(title, parent, action,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, ok_key, Gtk.ResponseType.OK))
        if filename:
            dialog.set_filename(filename)
        if purpose in ("save", "save_as"):
            dialog.props.do_overwrite_confirmation = True
        if file_types == "audio":
            file_types = [["Audio", "audio/*"]]
            dialog.set_preview_audio(True)
        elif file_types == "video":
            file_types = [["Video", "video/*"]]
        elif file_types == "image":
            file_types = [["Image", "image/*"]]
        elif file_types == "document":
            file_types = [["Document", "*.xml"]]

        for file_name, mime_type in file_types:
            if file_name == "Audio":
                dialog.set_preview_audio(True)
            filter_text = Gtk.FileFilter()
            filter_text.set_name("{0} files".format(file_name))
            if mime_type.find("/")>0:
                filter_text.add_mime_type(mime_type)
            else:
                filter_text.add_pattern(mime_type)
            dialog.add_filter(filter_text)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
        else:
            filename = None
        dialog.destroy()
        return filename


class FileSelect(Gtk.HBox):
    __gsignals__ = {
        'file-selected': (GObject.SIGNAL_RUN_FIRST, None,
                      tuple())
    }

    def __init__(self, file_types=[]):
        Gtk.HBox.__init__(self)
        self.selection_entry = Gtk.Entry()
        self.selection_entry.set_editable(False)

        self.select_button = Gtk.Button("S")
        self.select_button.connect("clicked", self.select_button_clicked)

        self.clear_button = Gtk.Button("C")
        self.clear_button.connect("clicked", self.clear_button_clicked)

        self.blank_button = Gtk.Button("B")
        self.blank_button.connect("clicked", self.blank_button_clicked)

        self.file_types = file_types
        self.set_filename(None)

        self.pack_start(self.selection_entry, expand=True, fill=True, padding=0)
        self.pack_end(self.clear_button, expand=False, fill=True, padding=0)
        self.pack_end(self.blank_button, expand=False, fill=True, padding=0)
        self.pack_end(self.select_button, expand=False, fill=True, padding=0)

    def set_filename(self, filename):
        if filename is None:
            filename = ""
        self.filename = filename
        self.selection_entry.set_text(filename)
        self.selection_entry.set_position(-1)

    def get_filename(self):
        return self.filename

    def select_button_clicked(self, widget):
        filename = FileOp.choose_file(widget.get_toplevel(), "open", self.file_types, filename=self.filename)
        if filename:
            self.set_filename(filename)
            self.emit("file-selected")

    def clear_button_clicked(self, widget):
        self.set_filename(None)
        self.emit("file-selected")

    def blank_button_clicked(self, widget):
        self.set_filename("//")
        self.emit("file-selected")

class FileChooserDialog(Gtk.FileChooserDialog):
    def __init__(self, *args, **kwargs):
        Gtk.FileChooserDialog.__init__(self, *args, **kwargs)
        self.connect("update-preview", self.file_selection_changed)
        self.file_type = None
        self.audio_player = None
        self.audio_jack = None
        self.audio_file_segment = None
        self.preview_audio = False

    def set_preview_audio(self, value):
        self.preview_audio = value

    def file_selection_changed(self, widget):
        if self.preview_audio:
            audio_jack = AudioJack.get_thread()
            if not audio_jack or not audio_jack.attached:
                return
            audio_jack.clear_all_audio_queues()
            if not self.audio_player:
                self.audio_player = AudioPlayer(10)
                self.audio_player.start()
            if self.audio_file_segment:
                self.audio_player.remove_segment(self.audio_file_segment)
                self.audio_file_segment = None
            filename = self.get_filename()
            self.audio_player.reset_time()
            if filename:
                self.audio_file_segment = AudioFileSegment(filename)
                self.audio_player.add_segment(self.audio_file_segment)

    def destroy(self):
        if self.audio_player:
            self.audio_player.should_stop = True
            if self.audio_player.is_alive():
                self.audio_player.join()
            self.audio_player = None
        super(FileChooserDialog, self).destroy()
