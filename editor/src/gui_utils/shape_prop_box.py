from gi.repository import Gtk, Gdk
from name_value_combo_box import NameValueComboBox
from ..commons import Point, Color

PROP_TYPE_NUMBER_ENTRY = 0
PROP_TYPE_COLOR = 1
PROP_TYPE_NAME_ENTRY = 2
PROP_TYPE_TEXT_LIST = 3
PROP_TYPE_POINT = 4

class ShapePropBox(Gtk.VBox):
    def __init__(self, draw_callback, shape_name_checker, insert_time_slice_callback):
        Gtk.VBox.__init__(self)
        self.prop_boxes = dict()
        self.prop_object = None
        self.draw_callback = draw_callback
        self.shape_name_checker = shape_name_checker
        self.insert_time_slice_callback = insert_time_slice_callback

    def set_prop_object(self, prop_object):
        self.prop_object = prop_object
        for prop_name in self.prop_boxes.keys():
            prop_widget = self.prop_boxes[prop_name]
            value = self.prop_object.get_prop_value(prop_name)
            if value is None: return
            if isinstance(prop_widget, Gtk.SpinButton):
                prop_widget.set_value(value)
            elif isinstance(prop_widget, Gtk.ColorButton):
                prop_widget.set_rgba(Gdk.RGBA(*value.get_array()))
            elif isinstance(prop_widget, Gtk.Entry):
                if prop_widget.value_type == PROP_TYPE_POINT:
                    value = value.to_text()
                prop_widget.set_text(value)

    def add_prop(self, prop_name, value_type, values):
        can_insert_slice = True
        if value_type == PROP_TYPE_NUMBER_ENTRY:
            adjustment = Gtk.Adjustment(values["value"], values["lower"],
                    values["upper"], values["step_increment"], values["page_increment"],
                    values["page_size"])
            spin_button = Gtk.SpinButton()
            spin_button.set_digits(2)
            spin_button.set_numeric(True)
            spin_button.set_adjustment(adjustment)
            spin_button.connect("value-changed", self.spin_button_value_changed, prop_name)
            prop_widget = spin_button
        elif value_type == PROP_TYPE_COLOR:
            color_button = Gtk.ColorButton()
            color_button.set_use_alpha(True)
            color_button.connect("color-set", self.color_button_value_changed, prop_name)
            prop_widget = color_button
        elif value_type == PROP_TYPE_POINT:
            point_entry = Gtk.Entry()
            point_entry.connect("changed", self.point_entry_value_changed, prop_name)
            prop_widget = point_entry
        elif value_type == PROP_TYPE_NAME_ENTRY:
            can_insert_slice = False
            entry = Gtk.Entry()
            entry.connect("activate", self.shape_name_entry_activated, prop_name)
            prop_widget = entry
        elif value_type == PROP_TYPE_TEXT_LIST:
            combo_box= NameValueComboBox()
            combo_box.connect("changed", self.combo_box_changed, prop_name)
            prop_widget = combo_box

        prop_widget.value_type = value_type

        label = Gtk.Label(prop_name)
        label.set_size_request(50, -1)
        prop_widget.set_size_request(150, -1)

        hbox = Gtk.HBox()
        hbox.pack_start(label, expand=False, fill=False, padding =0)
        hbox.pack_start(prop_widget, expand=False, fill=False, padding =5)

        if can_insert_slice:
            insert_slice_button = Gtk.Button("I+I")
            insert_slice_button.connect("clicked", self.insert_slice_button_clicked, prop_name)
            hbox.pack_start(insert_slice_button, expand=False, fill=False, padding =5)

        self.pack_start(hbox, expand=False, fill=False, padding = 5)
        self.prop_boxes[prop_name] = prop_widget
        return prop_widget

    def insert_slice_button_clicked(self, widget, prop_name):
        if self.prop_object != None:
            value = self.prop_object.get_prop_value(prop_name)
            self.insert_time_slice_callback(self.prop_object, prop_name, value)

    def shape_name_entry_activated(self, widget, prop_name):
        if self.prop_object != None:
            text = widget.get_text()
            if not self.shape_name_checker.set_shape_name(self.prop_object, text):
                widget.set_text(self.prop_object.get_prop_value(prop_name))

    def spin_button_value_changed(self, spin_button, prop_name):
        if self.prop_object != None:
            self.prop_object.set_prop_value(prop_name, spin_button.get_value())
            self.draw_callback()

    def color_button_value_changed(self, color_button, prop_name):
        if self.prop_object != None:
            rgba = color_button.get_rgba()
            color = Color(rgba.red, rgba.green, rgba.blue, rgba.alpha)
            self.prop_object.set_prop_value(prop_name, color)
            self.draw_callback()

    def point_entry_value_changed(self, point_entry, prop_name):
        if self.prop_object != None:
            point = Point.from_text(point_entry.get_text())
            self.prop_object.set_prop_value(prop_name, point)
            self.draw_callback()

    def combo_box_changed(self, combo_box, prop_name):
        if self.prop_object != None:
            value = combo_box.get_value()
            if value:
                self.prop_object.set_prop_value(prop_name, value)
                self.draw_callback()

