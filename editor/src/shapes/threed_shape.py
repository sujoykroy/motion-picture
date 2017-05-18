from ..commons import *
from shape import Shape
from rectangle_shape import RectangleShape

class ThreeDShape(Shape):
    TYPE_NAME = "threed"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius):
        super(ThreeDShape, self).__init__(anchor_at, border_color, border_width, fill_color, width, height, corner_radius)
        self.filepath = None
        self.image_canvas = None
        self.d3_object = Container3d()
        self.camera = Camera3d()

    def copy(self, copy_name=False, deep_copy=False):
        newob = ThreeDShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                        self.fill_color.copy(), self.width, self.height, self.corner_radius)
        self.copy_into(newob, copy_name)
        return newob

    def set_filepath(self, filepath):
        self.filepath = filepath
        self.d3_object.load_from_file(filename)
        self.camera.sort_items_from(self.d3_object)

    def build_image(self):
        self.image_canvas = self.camera.get_image_canvas(self.width, self.height)

    def draw_image(ctx):
        if self.image_canvas is None:
            return
        ctx.set_source_surface(self.image_canvas)
        ctx.paint()
