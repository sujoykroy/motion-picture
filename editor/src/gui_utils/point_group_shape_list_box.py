from gi.repository import Gtk
from name_value_combo_box import NameValueComboBox

class PointGroupShapeListBox(object):
    def __init__(self, select_callback):
        self.select_callback = select_callback

        self.label = Gtk.Label("Point Groups")
        self.label.set_halign(Gtk.Align.START)
        self.shape_list_combo_box = NameValueComboBox()
        self.shape_list_combo_box.connect("changed", self.point_group_selected)

    def set_shape_list(self, shapes_model):
        self.shape_list_combo_box.build_and_set_model(shapes_model)

    def point_group_selected(self, widget):
        point_group_shape = self.shape_list_combo_box.get_value()
        self.select_callback(point_group_shape)

    def hide(self):
        self.label.hide()
        self.shape_list_combo_box.hide()

    def show(self):
        self.label.show()
        self.shape_list_combo_box.show()
