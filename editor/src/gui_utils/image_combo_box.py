from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

class ImageComboBox(Gtk.ComboBox):
    def __init__(self):
        Gtk.ComboBox.__init__(self)
        renderer_pixbuf = Gtk.CellRendererPixbuf()
        self.pack_start(renderer_pixbuf, True)
        self.add_attribute(renderer_pixbuf, "pixbuf", 0)
        renderer_text = Gtk.CellRendererText()
        self.pack_start(renderer_text, True)
        self.add_attribute(renderer_text, "text", 1)
        self.values_dict = dict()

    def build_and_set_model(self, values):
        self.values_dict.clear()
        store = Gtk.ListStore(Pixbuf, str)
        if values:
            for value in values:
                store.append([value.get_pixbuf(), value.get_name()])
                self.values_dict[value.get_id()] = value
        self.set_model(store)
        self.set_id_column(1)

    def set_value(self, value):
        if value in self.values_dict:
            self.set_active_id(value)

    def get_value(self, default=None):
        active_id = self.get_active_id()
        if active_id is not None:
            return self.values_dict[active_id].get_id()
        return default

