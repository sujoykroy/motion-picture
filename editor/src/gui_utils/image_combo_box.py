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
                if isinstance(value, list):
                    store.append([value[0], value[1]])
                    self.values_dict[value[1]] = value[1]
                else:
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
            value_ob = self.values_dict[active_id]
            if hasattr(value_ob, "get_id"):
                return value_ob.get_id()
            return value_ob
        return default

