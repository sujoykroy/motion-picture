from ..commons import *
from shape import Shape
from rectangle_shape import RectangleShape
import math
DEG2PI = math.pi/180.

class ThreeDShape(RectangleShape):
    TYPE_NAME = "threed"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius):
        super(ThreeDShape, self).__init__(anchor_at, border_color, border_width, fill_color, width, height, corner_radius)
        self.filepath = None
        self.image_canvas = None
        self.d3_object = Container3d()
        self.camera = Camera3d()
        self.camera.rotate_deg((-120, 0, -20))
        self.should_rebuild_d3 = True
        self.should_rebuild_camera = True
        self.should_rebuild_image = True
        self.wire_color = None
        self.wire_width = None

    def copy(self, copy_name=False, deep_copy=False):
        newob = ThreeDShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                        self.fill_color.copy(), self.width, self.height, self.corner_radius)
        self.copy_into(newob, copy_name)
        return newob

    def get_object_scale(self):
        return self.d3_object.scale.get_average()

    def set_object_scale(self, value):
        self.d3_object.scale.set_average(value)
        self.should_rebuild_d3 = True

    def get_camera_rotate_x(self):
        return self.camera.rotation.get_x()/DEG2PI

    def get_camera_rotate_y(self):
        return self.camera.rotation.get_y()/DEG2PI

    def get_camera_rotate_z(self):
        return self.camera.rotation.get_z()/DEG2PI

    def set_camera_rotate_x(self, value):
        self.camera.rotation.set_x(value*DEG2PI)
        self.should_rebuild_camera = True

    def set_camera_rotate_y(self, value):
        self.camera.rotation.set_y(value*DEG2PI)
        self.should_rebuild_camera = True

    def set_camera_rotate_z(self, value):
        self.camera.rotation.set_z(value*DEG2PI)
        self.should_rebuild_camera = True

    def set_width(self, value):
        super(ThreeDShape, self).set_width(value)
        self.should_rebuild_image = True

    def set_height(self, value):
        super(ThreeDShape, self).set_height(value)
        self.should_rebuild_image = True

    def set_anchor_x(self, value):
        super(ThreeDShape, self).set_anchor_x(value)
        self.should_rebuild_image = True

    def set_anchor_y(self, value):
        super(ThreeDShape, self).set_anchor_y(value)
        self.should_rebuild_image = True

    def set_wire_color(self, color):
        if color is None:
            self.wire_color = None
        elif isinstance(self.wire_color, Color) and isinstance(color, Color):
            self.wire_color.copy_from(color)
        else:
            self.wire_color = color
        self.should_rebuild_image = True

    def set_wire_width(self, value):
        self.wire_width = value
        self.should_rebuild_image = True

    def set_filepath(self, filepath):
        self.filepath = filepath
        self.d3_object.load_from_file(self.filepath)

        self.should_rebuild_d3 = True
        self.should_rebuild_camera = True
        self.should_rebuild_image = True

    def build_image(self):
        self.d3_object.build_projection(self.camera)
        self.camera.sort_items(self.d3_object)
        self.image_canvas = self.camera.get_image_canvas(
            -self.anchor_at.x, -self.anchor_at.y,
            self.width, self.height,
            border_color=self.wire_color,
            border_width=self.wire_width
        )
        self.should_rebuild_d3 = False
        self.should_rebuild_camera = False
        self.should_rebuild_image = False

    def draw_image(self, ctx):
        if self.should_rebuild_d3:
            self.d3_object.precalculate()
        if self.should_rebuild_camera:
            self.camera.precalculate()
        if self.should_rebuild_d3 or self.should_rebuild_camera or self.should_rebuild_image:
            self.build_image()
        ctx.set_antialias(True)
        ctx.set_source_surface(self.image_canvas)
        ctx.get_source().set_filter(cairo.FILTER_FAST)
        ctx.paint()
