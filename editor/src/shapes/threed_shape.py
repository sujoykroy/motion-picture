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
        self.wire_width = 0
        self.high_quality = False
        self.image_hash = None

    def copy(self, copy_name=False, deep_copy=False):
        newob = ThreeDShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                        self.fill_color.copy(), self.width, self.height, self.corner_radius)
        self.copy_into(newob, copy_name)
        return newob

    def get_xml_element(self):
        elm = super(ThreeDShape, self).get_xml_element()
        elm.attrib["filepath"] = self.filepath
        elm.attrib["camera_rotation"] = self.camera.rotation.to_text()
        elm.attrib["object_scale"] = "{0}".format(self.get_object_scale())
        if self.wire_color:
            elm.attrib["wire_color"] = self.wire_color.to_text()
        elm.attrib["wire_width"] = "{0}".format(self.wire_width)
        elm.attrib["high_quality"] = "{0}".format(int(self.high_quality))
        elm.append(self.d3_object.get_xml_element())
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        shape = super(ThreeDShape, cls).create_from_xml_element(elm)
        shape.camera.rotation = Point3d.from_text(elm.attrib["camera_rotation"])
        shape.wire_color = color_from_text(elm.attrib.get("wire_color", None))
        shape.wire_width = float(elm.attrib["wire_width"])
        shape.set_filepath(elm.attrib.get("filepath", ""), load_file=False)
        shape.high_quality = bool(int(elm.attrib["high_quality"]))
        shape.set_object_scale(float(elm.attrib["object_scale"]))

        container3d_elm = elm.find(Container3d.TAG_NAME)
        if container3d_elm and not shape.d3_object.items:
            shape.d3_object = Container3d.create_from_xml_element(container3d_elm)
        return shape

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
        if self.wire_color is not None:
           self.should_rebuild_image = True

    def set_filepath(self, filepath, load_file=True):
        self.filepath = filepath
        if not load_file:
            return
        self.d3_object.clear()
        self.d3_object.load_from_file(self.filepath)

        self.should_rebuild_d3 = True
        self.should_rebuild_camera = True
        self.should_rebuild_image = True

    def set_high_quality(self, hq):
        self.high_quality = hq
        self.should_rebuild_image = True
        self.image_hash = None

    def build_image(self, ctx=None):
        self.d3_object.build_projection(self.camera)
        self.camera.sort_items(self.d3_object)
        if self.high_quality and ctx is not None:
            self.image_canvas = self.camera.get_image_canvas_high_quality(
                ctx,
                -self.anchor_at.x, -self.anchor_at.y,
                self.width, self.height,
                border_color=self.wire_color,
                border_width=self.wire_width
            )
        else:
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
        ctx.set_antialias(True)

        ctx.save()
        if self.high_quality:
            w, h = ctx.get_target().get_width(), ctx.get_target().get_height()
            xx, yx, xy, yy, x0, y0 = ctx.get_matrix()
            image_hash = hash(tuple([w, h, xx, yx, xy, yy, x0, y0]))
            if self.image_hash is None or \
               self.image_hash != image_hash or \
               self.image_canvas is None or \
               self.should_rebuild_d3 or \
               self.should_rebuild_camera or \
               self.should_rebuild_image:
                self.build_image(ctx)
            self.image_hash = image_hash
        elif self.image_canvas is None or \
             self.should_rebuild_d3 or \
             self.should_rebuild_camera or \
             self.should_rebuild_image:
            self.build_image()
        ctx.restore()

        if self.high_quality:
            mat = ctx.get_matrix()
            ctx.set_matrix(cairo.Matrix())
            ctx.set_source_surface(self.image_canvas)
            ctx.paint()
            ctx.set_matrix(mat)
        else:
            ctx.set_source_surface(self.image_canvas)
            ctx.get_source().set_filter(cairo.FILTER_FAST)
            ctx.paint()
