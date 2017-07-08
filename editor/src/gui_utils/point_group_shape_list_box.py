from gi.repository import Gtk

class PointGroupShapeListBox(Gtk.Box):
    def __init__(self, select_callback):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.select_callback = select_callback

        self.shape_list_combo = NameValueComboBox()
        self.select_button = Gtk.Button("Select")
        self.select_button.connect("clicked", self.select_button_clicked)

        self.pack_start(Gtk.Label("Point Groups"), expand=False, fill=False, padding=0)
        self.pack_start(self.shape_list_combo, expand=False, fill=False, padding=0)
        self.pack_start(self.select_button, expand=False, fill=False, padding=0)

    def set_shape_list(self, shapes_model):
        self.shape_list_combo.build_and_set_model(shapes_model)

    def select_button_clicked(self):
        point_group_shape = self.shape_list_combo_box.get_value()
        if point_group_shape:
            self.select_callback(point_group_shape)

