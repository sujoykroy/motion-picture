from gi.repository import Gtk

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
