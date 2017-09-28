from gi.repository import Gtk, Gdk
from ..document import Document
import os

class RecentFilesManager(Gtk.Dialog):
    def __init__(self, parent, recent_files, width=400, height = 500):
        Gtk.Dialog.__init__(self, "Recent Files", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_size(width, height)

        box = self.get_content_area()
        scrolled_window = Gtk.ScrolledWindow()
        box.set_size_request(width, height)
        box.pack_start(scrolled_window, expand=True, fill=True, padding=0)

        vbox = Gtk.VBox()
        scrolled_window.add_with_viewport(vbox)
        self.active_button = None

        image_per_row = 4
        image_width = float(width-40)/image_per_row
        count = 0
        for i in range(len(recent_files)):
            filename = recent_files[i]
            if not os.path.isfile(filename): continue
            #print filename
            basename = os.path.basename(filename)
            if count%image_per_row == 0:
                hbox = Gtk.HBox()
                vbox.pack_start(hbox, expand=False, fill=False, padding=0)
            count += 1
            try:
                doc = Document(filename=filename)
            except:
                continue
            pixbuf = doc.get_pixbuf(width=image_width, height=100)
            image_widget = Gtk.Image.new_from_pixbuf(pixbuf)
            toggle_button = Gtk.ToggleButton.new()
            toggle_button.set_image(image_widget)
            toggle_button.set_tooltip_text(filename)
            toggle_button.connect("clicked", self.file_button_clicked)
            toggle_button.set_events(Gdk.EventMask.POINTER_MOTION_MASK|Gdk.EventMask.BUTTON_PRESS_MASK)
            toggle_button.connect("button-press-event", self.file_button_mouse_pressed)
            toggle_button.filename = filename

            label = Gtk.Label(basename)
            label.set_halign(.5)
            label.props.wrap = True
            label.props.wrap_mode = 2

            image_vbox = Gtk.VBox()
            hbox.pack_start(image_vbox, expand=False, fill=False, padding=0)

            image_vbox.pack_start(toggle_button, expand=False, fill=False, padding=0)
            image_vbox.pack_start(label, expand=False, fill=False, padding=0)

        self.props.resizable = False
        self.show_all()

    def file_button_clicked(self, widget):
        if self.active_button:
            self.active_button.props.active = False
        if widget != self.active_button:
            self.active_button = widget
        else:
            self.active_button = None

    def file_button_mouse_pressed(self, widget, event):
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            self.response(Gtk.ResponseType.OK)

    def get_filename(self):
        if not self.active_button: return None
        return self.active_button.filename
