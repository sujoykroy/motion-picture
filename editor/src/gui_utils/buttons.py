from .. import settings
from ..document import Document
from gi.repository import Gtk
import os

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
