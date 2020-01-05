from gi.repository import Gtk, Gdk
from ..document import Document
import os

class FileListPreview(Gtk.Window):
    def __init__(self, width=800, height=600, title="FileList", on_file_select=None):
        Gtk.Window.__init__(self, title=title, resizable=False, type=Gtk.WindowType.TOPLEVEL)
        self.set_default_size(width, height)
        self.width = width
        self.connect("delete-event", self.quit)
        self.set_position(Gtk.WindowPosition.CENTER)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_size_request(width, height)
        self.add(scrolled_window)

        self.grid = Gtk.Grid()
        scrolled_window.add_with_viewport(self.grid)
        self.on_file_select = on_file_select

    def quit(self, widget, event):
        Gtk.main_quit()

    def show_files(self, folder, files, images_per_row=4):
        image_width = float(self.width-40)/images_per_row
        count = 0
        row = 0
        column = 0
        for i in range(len(files)):
            filename = files[i]
            fullpath = os.path.join(folder, filename)
            if not os.path.isfile(fullpath): continue
            basename = os.path.basename(filename)
            doc = Document(filename=fullpath)
            pixbuf = doc.get_pixbuf(width=image_width, height=100)
            image_widget = Gtk.Image.new_from_pixbuf(pixbuf)
            button = Gtk.Button.new()
            button.set_image(image_widget)
            button.set_tooltip_text(filename)
            button.set_events(Gdk.EventMask.POINTER_MOTION_MASK|Gdk.EventMask.BUTTON_PRESS_MASK)
            button.connect("button-press-event", self.file_button_mouse_pressed)
            button.filename = fullpath

            label = Gtk.Label(basename)
            label.set_halign(.5)
            label.props.wrap = True
            label.props.wrap_mode = 2

            image_vbox = Gtk.VBox()
            image_vbox.pack_start(button, expand=False, fill=False, padding=0)
            image_vbox.pack_start(label, expand=False, fill=False, padding=0)

            self.grid.attach(image_vbox, left=column, top=row, width=1, height=1)
            column += 1
            if column==images_per_row:
                row += 1
                column = 0

        self.show_all()
        Gtk.main()

    def file_button_mouse_pressed(self, widget, event):
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            if self.on_file_select:
                self.on_file_select(widget.filename)

