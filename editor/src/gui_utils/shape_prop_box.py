from gi.repository import Gtk, Gdk
from name_value_combo_box import NameValueComboBox
from buttons import ColorButton
from ..commons import Point, Color, get_displayble_prop_name
from ..commons import LinearGradientColor, RadialGradientColor

PROP_TYPE_NUMBER_ENTRY = 0
PROP_TYPE_COLOR = 1
PROP_TYPE_NAME_ENTRY = 2
PROP_TYPE_TEXT_LIST = 3
PROP_TYPE_POINT = 4
PROP_TYPE_CHECK_BUTTON = 5
PROP_TYPE_LONG_TEXT = 6
PROP_TYPE_TEXT = 7
PROP_TYPE_FONT = 8

class ShapePropBox(object):
    def __init__(self, parent_window, draw_callback, shape_name_checker, insert_time_slice_callback):
        self.parent_window = parent_window
        self.prop_boxes = dict()
        self.prop_object = None
        self.draw_callback = draw_callback
        self.shape_name_checker = shape_name_checker
        self.insert_time_slice_callback = insert_time_slice_callback
        self.widget_rows = []

    def hide(self):
        self.show_widgets(False)

    def show(self):
        self.show_widgets(True)

    def show_widgets(self, visible):
        for widget_row in self.widget_rows:
            for widget in widget_row:
                if visible:
                    widget.show()
                else:
                    widget.hide()

    def add_into_grid(self, grid, start_row):
        r = start_row
        for widget_row in self.widget_rows:
            c = 0
            for widget in widget_row:
                if len(widget_row) == 2 and c == 1:
                    width=4
                else:
                    width = 1
                grid.attach(widget, left=c, top=r, width=width, height=1)
                c += 1
            r += 1
        return r

    def set_prop_object(self, prop_object):
        self.prop_object = prop_object
        for prop_name in self.prop_boxes.keys():
            prop_widget = self.prop_boxes[prop_name]
            if not self.prop_object.has_prop(prop_name):
                prop_widget.hide()
                for widget in prop_widget.widgets:
                    widget.hide()
                continue
            prop_widget.show()
            for widget in prop_widget.widgets:
                widget.show()
            value = self.prop_object.get_prop_value(prop_name)
            if value is None: continue
            if isinstance(prop_widget, Gtk.SpinButton):
                prop_widget.set_value(value)
            elif isinstance(prop_widget, ColorButton):
                prop_widget.reset()
                prop_widget.set_color(value)
            elif isinstance(prop_widget, Gtk.FontButton):
                prop_widget.set_font_name(value)
            elif isinstance(prop_widget, Gtk.TextView):
                prop_widget.get_buffer().set_text(value)
            elif isinstance(prop_widget, NameValueComboBox):
                prop_widget.set_value(value)
            elif isinstance(prop_widget, Gtk.Entry):
                if prop_widget.value_type == PROP_TYPE_POINT:
                    value = value.to_text()
                prop_widget.set_text(value)
            elif isinstance(prop_widget, Gtk.CheckButton):
                prop_widget.set_active(value)

    def add_prop(self, prop_name, value_type, values, can_insert_slice = True):
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
            color_button = ColorButton()
            color_button.connect("clicked", self.color_button_clicked, prop_name)
            color_button.connect("type-changed", self.color_button_color_type_changed, prop_name)
            color_button.connect("color-changed", self.color_button_color_changed, prop_name)
            prop_widget = color_button
        elif value_type == PROP_TYPE_FONT:
            can_insert_slice = False
            font_button = Gtk.FontButton()
            font_button.connect("font-set", self.font_button_font_set, prop_name)
            prop_widget = font_button
        elif value_type == PROP_TYPE_POINT:
            point_entry = Gtk.Entry()
            point_entry.connect("changed", self.point_entry_value_changed, prop_name)
            prop_widget = point_entry
            point_entry.props.width_chars = 10
        elif value_type == PROP_TYPE_NAME_ENTRY:
            can_insert_slice = False
            entry = Gtk.Entry()
            entry.props.width_chars = 10
            entry.connect("activate", self.shape_name_entry_activated, prop_name)
            prop_widget = entry
        elif value_type == PROP_TYPE_TEXT_LIST:
            combo_box= NameValueComboBox()
            combo_box.connect("changed", self.combo_box_changed, prop_name)
            prop_widget = combo_box
        elif value_type == PROP_TYPE_CHECK_BUTTON:
            check_button= Gtk.CheckButton()
            check_button.connect("clicked", self.check_button_clicked, prop_name)
            prop_widget = check_button
        elif value_type == PROP_TYPE_LONG_TEXT:
            text_view = Gtk.TextView()
            text_view.set_margin_top(2)
            text_view.set_margin_bottom(5)
            text_view.get_buffer().connect("changed", self.text_buffer_changed, prop_name, text_view)
            prop_widget = text_view
            can_insert_slice = False
        elif value_type == PROP_TYPE_TEXT:
            can_insert_slice = False
            entry = Gtk.Entry()
            entry.props.width_chars = 10
            entry.connect("activate", self.entry_activated, prop_name)
            prop_widget = entry

        prop_widget.value_type = value_type

        label = Gtk.Label(get_displayble_prop_name(prop_name))
        label.set_halign(Gtk.Align.START)
        prop_widget.widgets = []
        prop_widget.widgets.append(label)

        widgets = [label, prop_widget]

        if can_insert_slice:
            insert_slice_button = Gtk.Button("I+I")
            insert_slice_button.connect("clicked", self.insert_slice_button_clicked, prop_name)
            widgets.append(insert_slice_button)
            prop_widget.widgets.append(insert_slice_button)

            apply_on_poses_button = Gtk.Button("P")
            apply_on_poses_button.connect("clicked", self.apply_on_poses_button_clicked, prop_name)
            widgets.append(apply_on_poses_button)
            prop_widget.widgets.append(apply_on_poses_button)

        self.widget_rows.append(widgets)

        self.prop_boxes[prop_name] = prop_widget
        return prop_widget

    def font_button_font_set(self, font_button, prop_name):
        if self.prop_object != None:
            font = font_button.get_font_name()
            self.prop_object.set_prop_value(prop_name, font)
            self.draw_callback()

    def color_button_clicked(self, color_button, prop_name):
        if not self.prop_object: return
        color_type = color_button.get_color_type()
        if color_type == "Flat":
            value = self.prop_object.get_prop_value(prop_name)
            dialog = Gtk.ColorChooserDialog()
            rgba = Gdk.RGBA(*value.get_array())
            dialog.set_rgba(rgba)
            if dialog.run() == Gtk.ResponseType.OK:
                dialog.get_rgba(rgba)
                color = Color(rgba.red, rgba.green, rgba.blue, rgba.alpha)
                dialog.destroy()
                color_button.set_color(color)
            else:
                dialog.destroy()
        else:
            shape_manager = self.parent_window.get_shape_manager()
            shape_manager.toggle_color_editor(prop_name, color_type)
            self.parent_window.redraw()

    def color_button_color_type_changed(self, color_button, prop_name):
        if not self.prop_object: return
        color_type = color_button.get_color_type()
        shape_manager = self.parent_window.get_shape_manager()
        shape = shape_manager.get_selected_shape()
        if color_type == "Flat":
            color = Color(0, 0, 0, 0)
        elif color_type == "Linear":
            color = LinearGradientColor.create_default(shape.get_outline(0))
        elif color_type == "Radial":
            color = RadialGradientColor.create_default(shape.get_outline(0))
        if shape_manager and shape_manager.color_editor:
            shape_manager.color_editor = None
        color_button.set_color(color)

    def color_button_color_changed(self, color_button, prop_name):
        if self.prop_object != None:
            color = color_button.get_color()
            self.prop_object.set_prop_value(prop_name, color)
            self.draw_callback()

    def insert_slice_button_clicked(self, widget, prop_name):
        if self.prop_object != None:
            value = self.prop_object.get_prop_value(prop_name)
            self.insert_time_slice_callback(self.prop_object, prop_name, value)

    def apply_on_poses_button_clicked(self, widget, prop_name):
        if not self.prop_object or not hasattr(self.prop_object.parent_shape, "set_shape_prop_for_all_poses"):
            return
        self.prop_object.parent_shape.set_shape_prop_for_all_poses(self.prop_object, prop_name)

    def shape_name_entry_activated(self, widget, prop_name):
        if self.prop_object != None:
            text = widget.get_text()
            text = text.replace(".", "_")
            widget.set_text(text)
            if not self.shape_name_checker.set_shape_name(self.prop_object, text):
                widget.set_text(self.prop_object.get_prop_value(prop_name))

    def entry_activated(self, widget, prop_name):
        if self.prop_object != None:
            text = widget.get_text()
            self.prop_object.set_prop_value(prop_name, text)
            self.draw_callback()

    def spin_button_value_changed(self, spin_button, prop_name):
        if self.prop_object != None:
            self.prop_object.set_prop_value(prop_name, spin_button.get_value())
            self.draw_callback()

    def point_entry_value_changed(self, point_entry, prop_name):
        if self.prop_object != None:
            point = Point.from_text(point_entry.get_text())
            self.prop_object.set_prop_value(prop_name, point)
            self.draw_callback()

    def combo_box_changed(self, combo_box, prop_name):
        if self.prop_object != None:
            value = combo_box.get_value()
            self.prop_object.set_prop_value(prop_name, value)
            self.draw_callback()

    def check_button_clicked(self, check_button, prop_name):
        if self.prop_object != None:
            self.prop_object.set_prop_value(prop_name, check_button.get_active())
            self.draw_callback()

    def text_buffer_changed(self, text_buffer, prop_name, text_view):
        if self.prop_object != None:
            value = text_buffer.get_text(
                text_buffer.get_start_iter(), text_buffer.get_end_iter(), False)
            self.prop_object.set_prop_value(prop_name, value)
            self.draw_callback()
