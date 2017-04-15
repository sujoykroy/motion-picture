from gi.repository import Gtk, GObject

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

        dialog = Gtk.FileChooserDialog(title, parent, action,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, ok_key, Gtk.ResponseType.OK))
        if filename:
            dialog.set_filename(filename)
        if purpose in ("save", "save_as"):
            dialog.props.do_overwrite_confirmation = True

        if file_types == "audio":
            file_types = [["Audio", "audio/*"]]
        for file_name, mime_type in file_types:
            filter_text = Gtk.FileFilter()
            filter_text.set_name("{0} files".format(file_name))
            filter_text.add_mime_type(mime_type)
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
        self.select_button = Gtk.Button("C")
        self.select_button.connect("clicked", self.select_button_clicked)
        self.file_types = file_types
        self.set_filename(None)

        self.pack_start(self.selection_entry, expand=True, fill=True, padding=0)
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
