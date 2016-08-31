from ..commons import *
from rectangle_shape import RectangleShape
from gi.repository import Gdk, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf

class ImageShape(RectangleShape):
    TYPE_NAME = "Image"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius):
        RectangleShape.__init__(self, anchor_at, border_color, border_width,
                                fill_color, width, height, corner_radius)
        self.image_path = None
        self.image_pixbuf = None


    def set_image_path(self, image_path):
        print  image_path
        self.image_path = image_path
        self.image_pixbuf = Pixbuf.new_from_file(image_path)

    def draw_image(self, ctx):
        if self.image_pixbuf:
            ctx.save()
            ctx.scale(self.width/float(self.image_pixbuf.get_width()),
                      self.height/float(self.image_pixbuf.get_height()))
            Gdk.cairo_set_source_pixbuf(ctx, self.image_pixbuf, 0, 0)
            ctx.paint()
            ctx.restore()

