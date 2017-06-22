from ..commons import *
from rectangle_shape import RectangleShape, Shape
from gi.repository import Gdk, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf

class ImageShape(RectangleShape):
    TYPE_NAME = "Image"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius):
        RectangleShape.__init__(self, anchor_at, border_color, border_width,
                                fill_color, width, height, corner_radius)
        self.image_path = None
        self.image_pixbuf = None
        self.alpha = 1.

    def copy(self, copy_name=False, deep_copy=False):
        newob = ImageShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                        self.fill_color.copy(), self.width, self.height, self.corner_radius)
        self.copy_into(newob, copy_name)
        newob.set_image_path(self.image_path)
        newob.alpha = self.alpha
        return newob

    def get_xml_element(self):
        elm = RectangleShape.get_xml_element(self)
        elm.attrib["image_path"] = self.image_path
        elm.attrib["alpha"] = "{0}".format(self.alpha)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        shape = super(ImageShape, cls).create_from_xml_element(elm)
        shape.set_image_path(elm.attrib.get("image_path", ""))
        shape.alpha = float(elm.attrib.get("alpha", 1.))
        return shape

    def set_prop_value(self, prop_name, prop_value, prop_data=None):
        if prop_name == "alpha":
            self.set_alpha(prop_value, prop_data)
        else:
            super(ImageShape, self).set_prop_value(prop_name, prop_value, prop_data)

    def set_image_path(self, image_path):
        if self.image_path != image_path:
            self.image_path = image_path
            if image_path == "//":
                self.image_pixbuf = None
            elif image_path:
                try:
                    self.image_pixbuf = Pixbuf.new_from_file(image_path)
                except:
                    self.image_pixbuf = None

    def set_alpha(self, value, prop_data = None):
        if prop_data and "image_path" in prop_data:
            image_path = prop_data.get("image_path")
            self.set_image_path(image_path)

        self.alpha = value

    def draw_image(self, ctx, root_shape=None):
        if self.image_pixbuf:
            ctx.save()
            ctx.scale(self.width/float(self.image_pixbuf.get_width()),
                      self.height/float(self.image_pixbuf.get_height()))
            Gdk.cairo_set_source_pixbuf(ctx, self.image_pixbuf, 0, 0)
            if self.alpha<1:
                ctx.paint_with_alpha(self.alpha)
            else:
                ctx.paint()
            ctx.restore()

    def draw(self, ctx, fixed_border, root_shape=None):
        if self.fill_color is not None:
            ctx.save()
            self.pre_draw(ctx)
            self.draw_path(ctx, for_fill=True)
            self.draw_fill(ctx)
            ctx.restore()

        if self.border_color is not None:
            ctx.save()
            self.pre_draw(ctx)
            self.draw_path(ctx, for_fill=False)
            self.draw_image(ctx)
            if fixed_border:
                ctx.restore()
                self.draw_border(ctx)
            else:
                self.draw_border(ctx)
                ctx.restore()
