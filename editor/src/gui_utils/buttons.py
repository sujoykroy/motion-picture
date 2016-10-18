from .. import settings
from ..commons.colors import *
from ..commons import Rect
from ..commons.draw_utils import *
from ..document import Document
from gi.repository import Gtk, GdkPixbuf, GObject, Gdk
from name_value_combo_box import NameValueComboBox
import os, cairo

def create_new_image_button(icon_name, desc=None, border_scale=1.):
    if desc is None:
        desc = icon_name[0].upper() + icon_name[1:]
    image_widget = create_new_image_widget(icon_name, border_scale)
    if image_widget:
        button = Gtk.Button()
        button.set_image(image_widget)
        button.set_tooltip_text(desc)
    else:
        button = Gtk.Button(desc)
    return button

def create_new_image_widget(icon_name, border_scale=1.):
    filename = os.path.join(settings.ICONS_FOLDER, icon_name + ".xml")
    if os.path.isfile(filename):
        doc = Document(filename=filename)
        doc.main_multi_shape.scale_border_width(border_scale)
        pixbuf = doc.get_pixbuf(width=20, height=20)
        return Gtk.Image.new_from_pixbuf(pixbuf)
    return None

class ColorButton(Gtk.HBox):
    def __init__(self):
        Gtk.HBox.__init__(self)
        self.color = None
        self.color_type = None

        self.color_button = Gtk.Button()
        self.pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 64, 20)
        self.image = Gtk.Image.new_from_pixbuf(self.pixbuf)
        self.image.set_margin_top(3)
        self.image.set_margin_bottom(3)
        self.color_button.set_image(self.image)
        self.color_button.connect("clicked", self.color_button_clicked)

        self.color_types_combobox =  NameValueComboBox()
        self.color_types_combobox.build_and_set_model(["Flat", "Linear", "Radial"])
        self.color_types_combobox.connect("changed", self.color_types_combobox_changed)

        self.pack_start(self.color_types_combobox, expand=False, fill=False, padding = 0)
        self.pack_start(self.color_button, expand=False, fill=False, padding = 0)

    def reset(self):
        self.color_type = None
        self.color = None

    def color_button_clicked(self, widget):
        self.emit("clicked")

    def color_types_combobox_changed(self, widget):
        changed = (self.color_type != widget.get_value())
        self.color_type = widget.get_value()
        if changed:
            self.emit("type-changed")

    def get_color_type(self):
        return self.color_type

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color
        if not color:
            color = Color(0,0,0,.1)
        if isinstance(color, Color):
            self.pixbuf.fill(int(color.to_html()[1:], 16))
            self.color_type = "Flat"
        elif isinstance(color, GradientColor):
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                self.pixbuf.get_width(), self.pixbuf.get_height())
            ctx = cairo.Context(surface)
            Gdk.cairo_set_source_pixbuf(ctx, self.pixbuf, 0, 0)
            ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)

            rect = Rect.create_from_points(color.color_points[0].point, color.color_points[-1].point)
            if rect.width == 0:
                rect.width = 1.
            if rect.height == 0:
                rect.height = 1.
            ctx.scale(self.pixbuf.get_width()/rect.width, self.pixbuf.get_height()/rect.height)
            set_default_line_style(ctx)
            ctx.rectangle(0, 0, rect.width, rect.height)
            draw_fill(ctx, color)

            surface= ctx.get_target()
            self.pixbuf= Gdk.pixbuf_get_from_surface(surface, 0, 0,
                    surface.get_width(), surface.get_height())
            self.image.set_from_pixbuf(self.pixbuf)
            if isinstance(color, RadialGradientColor):
                self.color_type = "Radial"
            elif isinstance(color, LinearGradientColor):
                self.color_type = "Linear"

        self.color_types_combobox.set_value(self.color_type)
        self.emit("color-changed")

GObject.signal_new('clicked', ColorButton,
        GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, tuple())
GObject.signal_new('type-changed', ColorButton,
        GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, tuple())
GObject.signal_new('color-changed', ColorButton,
        GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, tuple())
