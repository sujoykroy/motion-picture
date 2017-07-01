from gi.repository import Gtk
from name_value_combo_box import NameValueComboBox
from ..time_lines.time_change_types import *
from ..commons import get_displayble_prop_name, Text
from file_op import *
from buttons import create_new_image_button

class TimeSlicePropBox(Gtk.Frame):
    NUMBER = 0
    BOOLEAN = 1
    TEXT = 2
    LIST = 3
    NUMBERS = 4
    AUDIO_FILE = 5
    VIDEO_FILE = 6
    IMAGE_FILE = 7
    DOCUMENT_FILE = 8

    def __init__(self, draw_callback):
        Gtk.Frame.__init__(self)
        self.set_margin_left(10)
        self.set_margin_right(10)

        self.set_name("frame")
        self.set_label("Time Slice Properties")
        self.draw_callback = draw_callback
        self.attrib_widgets = dict()
        self.periodic_widgets = dict()
        self.loop_widgets = dict()
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
        self.add_editable_item("prop_data", "text", self.TEXT)
        self.add_editable_item("prop_data", "audio_path", self.AUDIO_FILE)
        self.add_editable_item("prop_data", "video_path", self.VIDEO_FILE)
        self.add_editable_item("prop_data", "image_path", self.IMAGE_FILE)
        self.add_editable_item("prop_data", "follow_curve", self.TEXT)
        self.add_editable_item("prop_data", "follow_angle", self.BOOLEAN)
        self.add_editable_item("prop_data", "document_path", self.DOCUMENT_FILE)
        self.add_editable_item("prop_data", "time_line_name", self.TEXT)
        self.add_editable_item("prop_data", "camera", self.TEXT)

        self.add_editable_item("attrib", "start_value", self.NUMBERS, syncable=True)
        self.add_editable_item("attrib", "end_value", self.NUMBERS, syncable=True)
        self.add_editable_item("attrib", "duration", self.NUMBER)
        self.add_editable_item("attrib", "end_marker", self.LIST)
        self.add_editable_item("attrib", "linked_to_next", self.BOOLEAN)
        self.add_editable_item("attrib", "change_type_class", self.LIST)

        self.add_editable_item("periodic", "period", self.NUMBER)
        self.add_editable_item("periodic", "phase", self.NUMBER)
        self.add_editable_item("periodic", "amplitude",self.NUMBER)

        self.add_editable_item("loop", "loop_count",self.NUMBER)

        combo = self.attrib_widgets["change_type_class"]
        combo.build_and_set_model([
            ["Linear", TimeChangeType],
            ["Sine", SineChangeType],
            ["Triangle", TriangleChangeType],
            ["Loop", LoopChangeType]
        ])
        self.time_markers = None

    def set_time_slice_box(self, time_slice_box):
        self.time_slice_box = time_slice_box
        if time_slice_box:
            self.time_slice = time_slice_box.time_slice
            self.prop_name = time_slice_box.prop_time_line_box.prop_time_line.prop_name
            self.shape = time_slice_box.prop_time_line_box.prop_time_line.shape
            self.update()
            self.show()
        else:
            self.shape = None
            self.time_slice = None
            self.hide()

    def set_time_markers(self, values):
        self.attrib_widgets["end_marker"].build_and_set_model([""] + sorted(values))

    def update(self, widget=None):
        if not self.time_slice: return

        if widget is None or widget.item_name == "change_type_class":
            if isinstance(self.time_slice.change_type, PeriodicChangeType):
                self.show_widgets(self.loop_widgets, False)
                self.show_widgets(self.periodic_widgets, True)
                self.show_values(self.periodic_widgets, self.time_slice.change_type)
            elif isinstance(self.time_slice.change_type, LoopChangeType):
                self.show_widgets(self.loop_widgets, True)
                self.show_widgets(self.periodic_widgets, False)
                self.show_values(self.loop_widgets, self.time_slice.change_type)
            else:
                self.show_widgets(self.loop_widgets, False)
                self.show_widgets(self.periodic_widgets, False)
        if widget is None:
            self.show_values(self.attrib_widgets, self.time_slice)

            prop_data = self.time_slice.prop_data
            if self.shape and prop_data:
                if "start_pose" in prop_data:
                    self.prop_data_widgets["start_pose"].build_and_set_model(sorted(self.shape.poses.keys()))
                if "end_pose" in prop_data or "start_pose" in prop_data:
                    self.prop_data_widgets["end_pose"].build_and_set_model(
                        [""] + sorted(self.shape.poses.keys()))
                if "pose" in prop_data:
                    self.prop_data_widgets["pose"].build_and_set_model(
                         [""] + sorted(self.shape.poses.keys()))
                if "timeline" in prop_data:
                    timelines = sorted(self.shape.timelines.keys())
                    timelines.insert(0, "")
                    self.prop_data_widgets["timeline"].build_and_set_model(timelines)
                if "start_form" in prop_data:
                    self.prop_data_widgets["start_form"].build_and_set_model(
                        [""] + sorted(self.shape.forms.keys()))
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
                    elif isinstance(widget, FileSelect):
                        widget.set_filename(prop_data[key])
                    elif isinstance(widget, Gtk.Entry):
                        widget.set_text(prop_data[key])
                    elif isinstance(widget, Gtk.CheckButton):
                        widget.set_active(prop_data[key])

            if self.prop_name == "internal" and "timeline" in self.time_slice.prop_data:
                widget = self.prop_data_widgets["camera"]
                widget.show()
                widget.label.show()
            if self.prop_name == "internal" and self.time_slice.prop_data["type"] == "pose":
                widget = self.prop_data_widgets["end_pose"]
                widget.show()
                widget.label.show()

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
                if hasattr(value, "to_text"):
                    value = value.to_text()
                widget.set_text("{0}".format(value))
            elif isinstance(widget, Gtk.CheckButton):
                widget.set_active(bool(value))
            elif isinstance(widget, NameValueComboBox):
                widget.set_value(value)
            elif isinstance(widget, FileSelect):
                widget.set_filename(value)

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

    def add_editable_item(self, source_name, item_name, item_type, syncable=False):
        label = Gtk.Label(get_displayble_prop_name(item_name))
        label.set_halign(Gtk.Align.START)

        if item_type in (self.NUMBER, self.NUMBERS):
            entry = Gtk.Entry()
            entry.connect("changed", self.item_widget_changed)
            item_widget = entry
        elif item_type == self.BOOLEAN:
            checkbox = Gtk.CheckButton()
            checkbox.connect("toggled", self.item_widget_changed)
            item_widget = checkbox
        elif item_type == self.LIST:
            combobox = NameValueComboBox()
            combobox.connect("changed", self.item_widget_changed)
            item_widget = combobox
        elif item_type == self.TEXT:
            entry = Gtk.Entry()
            entry.connect("changed", self.item_widget_changed)
            item_widget = entry
        elif item_type == self.AUDIO_FILE:
            file_chooser = FileSelect(file_types="audio")
            file_chooser.connect("file-selected", self.item_widget_changed)
            item_widget = file_chooser
        elif item_type == self.VIDEO_FILE:
            file_chooser = FileSelect(file_types="video")
            file_chooser.connect("file-selected", self.item_widget_changed)
            item_widget = file_chooser
        elif item_type == self.IMAGE_FILE:
            file_chooser = FileSelect(file_types="image")
            file_chooser.connect("file-selected", self.item_widget_changed)
            item_widget = file_chooser
        elif item_type == self.DOCUMENT_FILE:
            file_chooser = FileSelect(file_types="document")
            file_chooser.connect("file-selected", self.item_widget_changed)
            item_widget = file_chooser

        item_widget.item_type = item_type
        item_widget.item_name = item_name
        item_widget.source_name = source_name
        #item_widget.set_name("itemwidget")

        if source_name == "attrib":
            widgets_dict = self.attrib_widgets
        elif source_name == "periodic":
            widgets_dict = self.periodic_widgets
        elif source_name == "loop":
            widgets_dict = self.loop_widgets
        elif source_name == "prop_data":
            widgets_dict = self.prop_data_widgets

        self.grid.attach(label, left=0, top=self.grid_row_count, width=1, height=1)
        self.grid.attach(item_widget, left=1, top=self.grid_row_count, width=1, height=1)
        if syncable:
            sync_button = create_new_image_button("sync")
            sync_button.connect("clicked", self.sync_button_clicked, item_widget)
            self.grid.attach(sync_button, left=2, top=self.grid_row_count, width=1, height=1)
        self.grid_row_count += 1

        widgets_dict[item_name] = item_widget
        item_widget.label = label

        return item_widget

    def sync_button_clicked(self, widget, item_widget):
        if not self.time_slice:
            return
        value = self.shape.get_prop_value(self.prop_name)
        if value is None:
            return
        if hasattr(value, "copy"):
            value = value.copy()
        self.set_item_value_for_widget(item_widget, value, parse=False)
        self.update()

    def close_button_clicked(self, widget):
        self.hide()

    def set_item_value_for_widget(self, item_widget, value, parse):
        if item_widget.source_name == "periodic":
            source_object = self.time_slice.change_type
        elif item_widget.source_name == "loop":
            source_object = self.time_slice.change_type
        elif item_widget.source_name == "prop_data":
            source_object = self.time_slice.prop_data
        else:
            source_object = self.time_slice

        if parse:
            support_number_list = False
            if item_widget.item_type == self.NUMBERS:
                if self.shape.get_prop_type(self.prop_name) == "number_list":
                    support_number_list = True

            if item_widget.item_type == self.NUMBERS:
                if support_number_list:
                    value = Text.parse_number_list(value)
                    if not value:
                        return
                else:
                    value = Text.parse_number(value)
                    if value is None:
                        return
            elif item_widget.item_type == self.NUMBER:
                value = Text.parse_number(value)
                if value is None:
                    return
            elif item_widget.item_type == self.BOOLEAN:
                value = bool(value)

        self.set_item_value(source_object, item_widget.item_name, value)
        if item_widget.source_name == "attrib" and item_widget.item_name == "end_marker":
            self.time_slice_box.sync_with_time_marker(value)
            self.update()
            self.draw_callback()

    def item_widget_changed(self, widget):
        if not self.time_slice: return

        if isinstance(widget, Gtk.Entry):
            value = widget.get_text()
        elif isinstance(widget, Gtk.CheckButton):
            value = widget.get_active()
        elif isinstance(widget, NameValueComboBox):
            value = widget.get_value()
        elif isinstance(widget, FileSelect):
            value = widget.get_filename()

        self.set_item_value_for_widget(widget, value, parse=True)

        self.time_slice_box.update()
        self.time_slice_box.update_prev_linked_box()
        self.time_slice_box.update_next_linked_box()
        self.update(widget)
        self.draw_callback()
