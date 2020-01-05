from .. import settings
from ..commons import *
from ..document import Document
from gi.repository import Gtk, GdkPixbuf, GObject, Gdk
from .name_value_combo_box import NameValueComboBox
import os, cairo

def create_new_image_button(icon_name,
                desc=None, border_scale=1., size=20, button_class = Gtk.Button):
    if desc is None:
        desc = get_displayble_prop_name(icon_name)
    image_widget = create_new_image_widget(icon_name, border_scale, size=size)
    if image_widget:
        button = button_class()
        button.set_image(image_widget)
        button.set_tooltip_text(desc)
    else:
        button = Gtk.Button(desc)
    return button

def create_new_image_widget(icon_name, border_scale=1., size=20, desc=None):
    filename = os.path.join(settings.ICONS_FOLDER, icon_name + ".xml")
    if os.path.isfile(filename):
        doc = Document(filename=filename)
        doc.main_multi_shape.scale_border_width(border_scale)
        pixbuf = doc.get_pixbuf(width=size, height=size, bg_color=False)
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        if desc:
            image.set_tooltip_text(desc)
        return image
    return None

class EditingChoiceCheckWidget(Gtk.Box):
    def __init__(self, icon_name, choice_name, desc=None, border_scale=1.):
        Gtk.Box.__init__(self, Gtk.Orientation.HORIZONTAL)
        self.choice_name = choice_name

        self.pack_start(
            create_new_image_widget(icon_name, border_scale=border_scale),
            expand=False, fill=False, padding=5)

        self.check_button = Gtk.CheckButton()
        if not desc:
            desc = get_displayble_prop_name(icon_name)
        self.check_button.set_tooltip_text(desc)
        self.check_button.set_active(getattr(settings.EditingChoice, self.choice_name))
        self.check_button.connect("toggled", self.check_button_toggled)

        self.pack_start(self.check_button, expand=False, fill=False, padding=5)

    def check_button_toggled(self, widget):
        setattr(settings.EditingChoice, self.choice_name, self.check_button.get_active())

class ColorButton(Gtk.HBox):
    def __init__(self, color_types=["Flat", "Linear", "Radial", "Image"]):
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
        self.color_types_combobox.build_and_set_model(["None"] + color_types)
        self.color_types_combobox.set_value("None")
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
        surface = None
        ctx = None
        if color is None:
            self.color_type = "None"
            self.pixbuf.fill(int("00000000", 16))
        elif isinstance(color, Color):
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

            if isinstance(color, RadialGradientColor):
                self.color_type = "Radial"
            elif isinstance(color, LinearGradientColor):
                self.color_type = "Linear"
        elif isinstance(color, ImageColor):
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                self.pixbuf.get_width(), self.pixbuf.get_height())
            ctx = cairo.Context(surface)
            image_surface = color.get_surface()
            ctx.scale(
                self.pixbuf.get_width()*1./image_surface.get_width(),
                self.pixbuf.get_height()*1./image_surface.get_height())
            ctx.rectangle(0, 0, image_surface.get_width(), image_surface.get_height())
            draw_fill(ctx, color)

            self.color_type = "Image"

        if surface is not None and ctx is not None:
            surface= ctx.get_target()
            self.pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0,
                    surface.get_width(), surface.get_height())

        self.image.set_from_pixbuf(self.pixbuf)
        self.color_types_combobox.set_value(self.color_type)
        self.emit("color-changed")
        self.color_button.queue_draw()

GObject.signal_new('clicked', ColorButton,
        GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, tuple())
GObject.signal_new('type-changed', ColorButton,
        GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, tuple())
GObject.signal_new('color-changed', ColorButton,
        GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, tuple())
