from gi.repository import Gtk
from name_value_combo_box import NameValueComboBox
from ..time_lines.time_change_types import *
from ..commons import get_displayble_prop_name, Text

class TimeSlicePropBox(Gtk.Frame):
    NUMBER = 0
    BOOLEAN = 1
    TEXT = 2
    LIST = 3

    def __init__(self, draw_callback):
        Gtk.Frame.__init__(self)
        self.set_margin_left(10)
        self.set_margin_right(10)

        self.set_name("frame")
        self.set_label("Time Slice Properties")
        self.draw_callback = draw_callback
        self.attrib_widgets = dict()
        self.periodic_widgets = dict()
        self.prop_data_widgets = dict()

        self.time_slice = None
        self.time_slice_box = None

        #Todo
        self.close_button = Gtk.Button("x")
        self.close_button.connect("clicked", self.close_button_clicked)

        self.grid = Gtk.Grid()
        self.grid_row_count = 0
        self.add(self.grid)

        self.add_editable_item("prop_data", "start_pose", self.LIST)
        self.add_editable_item("prop_data", "end_pose", self.LIST)
        self.add_editable_item("prop_data", "pose", self.LIST)
        self.add_editable_item("prop_data", "timeline", self.LIST)
        self.add_editable_item("prop_data", "start_form", self.LIST)
        self.add_editable_item("prop_data", "end_form", self.LIST)

        self.add_editable_item("attrib", "start_value", self.NUMBER)
        self.add_editable_item("attrib", "end_value", self.NUMBER)
        self.add_editable_item("attrib", "duration", self.NUMBER)
        self.add_editable_item("attrib", "linked_to_next", self.BOOLEAN)
        self.add_editable_item("attrib", "change_type_class", self.LIST)

        self.add_editable_item("periodic", "period", self.NUMBER)
        self.add_editable_item("periodic", "phase", self.NUMBER)
        self.add_editable_item("periodic", "amplitude",self.NUMBER)

        combo = self.attrib_widgets["change_type_class"]
        combo.build_and_set_model([
            ["Linear", TimeChangeType],
            ["Sine", SineChangeType],
            ["Triangle", TriangleChangeType],
            ["Loop", LoopChangeType]
        ])

    def set_time_slice_box(self, time_slice_box):
        self.time_slice_box = time_slice_box
        if time_slice_box:
            self.time_slice = time_slice_box.time_slice
            self.shape = time_slice_box.prop_time_line_box.parent_box.shape_time_line.shape
            self.update()
            self.show()
        else:
            self.shape = None
            self.time_slice = None
            self.hide()

    def update(self, widget=None):
        if not self.time_slice: return

        if widget is None or widget.item_name == "change_type_class":
            if isinstance(self.time_slice.change_type, PeriodicChangeType):
                self.show_widgets(self.periodic_widgets, True)
                self.show_values(self.periodic_widgets, self.time_slice.change_type)
            else:
                self.show_widgets(self.periodic_widgets, False)
        if widget is None:
            self.show_values(self.attrib_widgets, self.time_slice)

            prop_data = self.time_slice.prop_data
            if self.shape and prop_data:
                if "start_pose" in prop_data:
                    self.prop_data_widgets["start_pose"].build_and_set_model(sorted(self.shape.poses.keys()))
                if "end_pose" in prop_data:
                    self.prop_data_widgets["end_pose"].build_and_set_model(
                        [""] + sorted(self.shape.poses.keys()))
                if "pose" in prop_data:
                    self.prop_data_widgets["pose"].build_and_set_model(sorted(self.shape.poses.keys()))
                if "timeline" in prop_data:
                    self.prop_data_widgets["timeline"].build_and_set_model(sorted(self.shape.timelines.keys()))
                if "start_form" in prop_data:
                    self.prop_data_widgets["start_form"].build_and_set_model(sorted(self.shape.forms.keys()))
                if "end_form" in prop_data:
                    self.prop_data_widgets["end_form"].build_and_set_model(
                        [""] + sorted(self.shape.forms.keys()))

            for key, widget in self.prop_data_widgets.items():
                if not prop_data or key not in prop_data:
                     widget.hide()
                     widget.label.hide()
                else:
                    widget.show()
                    widget.label.show()
                    if isinstance(widget, NameValueComboBox):
                        widget.set_value(prop_data[key])

    def show_widgets(self, widgets, visible):
        for key, widget in widgets.items():
            if visible:
                widget.label.show()
                widget.show()
            else:
                widget.label.hide()
                widget.hide()

    def show_values(self, widgets, obj):
        for key, widget in widgets.items():
            value = self.get_item_value(obj, key)
            if isinstance(widget, Gtk.Entry):
                widget.set_text("{0}".format(value))
            elif isinstance(widget, Gtk.CheckButton):
                widget.set_active(bool(value))
            elif isinstance(widget, NameValueComboBox):
                widget.set_value(value)

    def get_item_value(self, obj, name):
        if hasattr(obj, "get_prop_value"):
            func = getatrr(obj, "get_prop_value")
            return func(name)
        elif hasattr(obj, "get_" + name):
            func = getattr(obj, "get_" + name)
            return func()
        elif isinstance(obj, dict):
            return obj[name]
        return getattr(obj, name)

    def set_item_value(self, obj, name, value):
        if hasattr(obj, "set_prop_value"):
            func = getatrr(obj, "set_prop_value")
            func(name, value)
        elif hasattr(obj, "set_" + name):
            func = getattr(obj, "set_" + name)
            func(value)
        elif isinstance(obj, dict):
            obj[name] = value
        else:
            setattr(obj, name, value)

    def add_editable_item(self, source_name, item_name, item_type):
        label = Gtk.Label(get_displayble_prop_name(item_name))
        label.set_halign(Gtk.Align.START)

        if item_type == self.NUMBER:
            entry = Gtk.Entry()
            entry.connect("changed", self.item_widget_changed)
            item_widget = entry
            entry.props.max_length = 5
        elif item_type == self.BOOLEAN:
            checkbox = Gtk.CheckButton()
            checkbox.connect("toggled", self.item_widget_changed)
            item_widget = checkbox
        elif item_type == self.LIST:
            combobox = NameValueComboBox()
            combobox.connect("changed", self.item_widget_changed)
            item_widget = combobox

        item_widget.item_type = item_type
        item_widget.item_name = item_name
        item_widget.source_name = source_name
        #item_widget.set_name("itemwidget")

        if source_name == "attrib":
            widgets_dict = self.attrib_widgets
        elif source_name == "periodic":
            widgets_dict = self.periodic_widgets
        elif source_name == "prop_data":
            widgets_dict = self.prop_data_widgets

        self.grid.attach(label, left=0, top=self.grid_row_count, width=1, height=1)
        self.grid.attach(item_widget, left=1, top=self.grid_row_count, width=1, height=1)
        self.grid_row_count += 1

        widgets_dict[item_name] = item_widget
        item_widget.label = label

        return item_widget

    def close_button_clicked(self, widget):
        self.hide()

    def item_widget_changed(self, widget):
        if not self.time_slice: return

        if isinstance(widget, Gtk.Entry):
            value = widget.get_text()
        elif isinstance(widget, Gtk.CheckButton):
            value = widget.get_active()
        elif isinstance(widget, NameValueComboBox):
            value = widget.get_value()

        if widget.item_type == self.NUMBER:
            try:
                value = float(value)
            except ValueError as e:
                return
        elif widget.item_type == self.BOOLEAN:
            value == bool(value)

        if widget.source_name == "periodic":
            self.set_item_value(self.time_slice.change_type, widget.item_name, value)
        elif widget.source_name == "prop_data":
            self.set_item_value(self.time_slice.prop_data, widget.item_name, value)
        else:
            self.set_item_value(self.time_slice, widget.item_name, value)

        self.time_slice_box.update()
        self.time_slice_box.update_prev_linked_box()
        self.time_slice_box.update_next_linked_box()
        self.update(widget)
        self.draw_callback()
