from gi.repository import Gtk
from file_op import FileSelect
from name_value_combo_box import NameValueComboBox
from ..commons import ImageColor

class ImageColorDialog(Gtk.Dialog):
    def __init__(self, parent, color, color_button, width=400, height = 200):
        Gtk.Dialog.__init__(self, "Image Color", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_size(width, height)
        self.color_button = color_button
        self.color = color
        self.filename = color.filename
        self.offset_x = color.x
        self.offset_y = color.y

        box = self.get_content_area()

        label = Gtk.Label("Image File")
        box.pack_start(label, expand=False, fill=False, padding= 0)
        self.file_select = FileSelect()
        self.file_select.set_filename(self.filename)
        self.file_select.connect("file-selected", self.file_selected)
        box.pack_start(self.file_select, expand=False, fill=False, padding= 0)

        box.pack_start(Gtk.Label("Shape"), expand=False, fill=False, padding= 0)
        self.shape_entry = Gtk.Entry()
        self.shape_entry.set_text(color.shape_name)
        self.shape_entry.connect("changed", self.shape_entry_changed)
        box.pack_start(self.shape_entry, expand=False, fill=False, padding= 0)

        self.x_spin = Gtk.SpinButton()
        self.x_spin.set_range(-1000000, 100000)
        self.x_spin.set_increments(1, 1)
        self.x_spin.set_value(color.y)
        self.x_spin.connect("value-changed", self.spin_button_value_changed)

        self.y_spin = Gtk.SpinButton()
        self.y_spin.set_range(-1000000, 100000)
        self.y_spin.set_value(color.y)
        self.y_spin.set_increments(1, 1)
        self.y_spin.connect("value-changed", self.spin_button_value_changed)

        box.pack_start(Gtk.Label("Offset X"), expand=False, fill=False, padding= 0)
        box.pack_start(self.x_spin, expand=False, fill=False, padding= 0)

        box.pack_start(Gtk.Label("Offset Y"), expand=False, fill=False, padding= 0)
        box.pack_start(self.y_spin, expand=False, fill=False, padding= 0)

        box.pack_start(Gtk.Label("Extend Type"), expand=False, fill=False, padding= 0)
        self.extend_combo = NameValueComboBox()
        self.extend_combo.build_and_set_model(["None", "Repeat", "Reflect", "Pad"])
        self.extend_combo.set_value(color.extend_type[0].upper()+color.extend_type[1:])
        box.pack_start(self.extend_combo, expand=False, fill=False, padding= 0)

        self.show_all()

    def spin_button_value_changed(self, widget):
        self.preview()

    def shape_entry_changed(self, widget):
        self.preview()

    def file_selected(self, widget):
        self.filename = widget.filename
        self.preview()

    def get_image_color(self):
        color = ImageColor(
                filename = self.filename,
                shape_name = self.shape_entry.get_text().decode("utf-8"),
                extend_type=self.extend_combo.get_value().lower(),
                x=self.x_spin.get_value(), y=self.y_spin.get_value())
        color.set_owner_shape(self.color.owner_shape)
        return color

    def preview(self):
        self.color_button.set_color(self.get_image_color())
