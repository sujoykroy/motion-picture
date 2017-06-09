from ..commons import *
from shape import Shape
from rectangle_shape import RectangleShape

import math, time
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
        self.quality_scale = .25

    def copy(self, copy_name=False, deep_copy=False):
        newob = ThreeDShape(self.anchor_at.copy(), copy_value(self.border_color),
                        copy_value(self.border_width), copy_value(self.fill_color),
                        self.width, self.height, self.corner_radius)
        self.copy_into(newob, copy_name)
        return newob

    def get_xml_element(self):
        elm = super(ThreeDShape, self).get_xml_element()
        elm.attrib["filepath"] = self.filepath
        elm.attrib["camera_rotation"] = self.camera.rotation.to_text(factor=1/DEG2PI)
        if self.wire_color:
            elm.attrib["wire_color"] = self.wire_color.to_text()
        elm.attrib["wire_width"] = "{0}".format(self.wire_width)
        elm.attrib["high_quality"] = "{0}".format(int(self.high_quality))
        elm.attrib["quality_scale"] = "{0}".format(self.quality_scale)
        elm.append(self.d3_object.get_xml_element(exclude_border_fill=True))
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        shape = super(ThreeDShape, cls).create_from_xml_element(elm)
        shape.camera.rotation = Point3d.from_text(elm.attrib["camera_rotation"], factor=DEG2PI)
        shape.wire_color = color_from_text(elm.attrib.get("wire_color", None))
        shape.wire_width = float(elm.attrib["wire_width"])
        shape.set_filepath(elm.attrib.get("filepath", ""), load_file=False)
        shape.high_quality = bool(int(elm.attrib["high_quality"]))
        shape.set_quality_scale(float(elm.attrib.get("quality_scale", shape.quality_scale)))

        container3d_elm = elm.find(Container3d.TAG_NAME)
        if container3d_elm and not shape.d3_object.items:
            shape.d3_object = Container3d.create_from_xml_element(container3d_elm)
            shape.d3_object.set_border_color(shape.wire_color)
            shape.d3_object.set_border_width(shape.wire_width)
        return shape

    def get_object_scale(self):
        return self.d3_object.scale.get_average()

    def set_object_scale(self, value):
        self.d3_object.scale.set_average(value)
        self.should_rebuild_d3 = True

    def set_viewer_z(self, value):
        self.camera.viewer.set_z(value)
        self.should_rebuild_d3 = True
        self.should_rebuild_camera = True

    def get_viewer_z(self):
        return self.camera.viewer.get_z()

    def get_camera_position_z(self):
        return self.camera.translation.get_z()

    def set_camera_position_z(self, value):
        self.camera.translation.set_z(value)
        self.should_rebuild_d3 = True
        self.should_rebuild_camera = True

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

    def set_angle(self, value):
        super(ThreeDShape, self).set_angle(value)
        self.should_rebuild_image = True

    def move_to(self, x, y):
        super(ThreeDShape, self).move_to(x, y)
        self.should_rebuild_image = True

    def set_wire_color(self, color):
        if color is None:
            self.wire_color = None
        elif isinstance(self.wire_color, Color) and isinstance(color, Color):
            self.wire_color.copy_from(color)
        else:
            self.wire_color = color
        self.d3_object.set_border_color(self.wire_color)
        self.should_rebuild_image = True

    def set_wire_width(self, value):
        self.wire_width = value
        if self.wire_color is not None:
           self.should_rebuild_image = True
        self.d3_object.set_border_width(self.wire_width)

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

    def set_quality_scale(self, value):
        if int(value*self.width)<=0 or int(value*self.height)<=0:
            return
        self.quality_scale = value
        if not self.high_quality:
            self.should_rebuild_image = True

    def build_image(self, ctx=None):
        self.last_built_at = time.time()
        self.d3_object.build_projection(self.camera)
        self.camera.sort_items(self.d3_object)

        ay = self.anchor_at.y
        iay = self.height -ay

        if ay<iay:
            origin_y = iay
            canvas_height = 2*iay
        else:
            origin_y = ay
        canvas_height = 2*origin_y

        if self.high_quality:
            rect = self.get_abs_reverse_outline(0, 0, self.width, self.height)

            blank_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
            ctx = cairo.Context(blank_surface)
            ctx.translate(-rect.left, -rect.top)
            self.pre_draw(ctx)
            ctx.translate(self.anchor_at.x, self.anchor_at.y)
            ctx.scale(1, -1)
            premat = ctx.get_matrix()
            del blank_surface

            self.image_canvas = self.camera.get_image_canvas_high_quality(
                rect.width, rect.height,
                premat,
                -self.anchor_at.x, -self.anchor_at.y,#what happens to y?
                self.width, self.height,
                border_color=self.wire_color,
                border_width=self.wire_width
            )
            """
            ctx = cairo.Context(self.image_canvas)
            ctx.set_matrix(premat)
            ctx.rectangle(-2, -2, 4, 4)
            ctx.set_matrix(cairo.Matrix())
            draw_stroke(ctx, 4, "000000")
            """
        else:
            inv_canvas = self.camera.get_image_canvas(
                -self.anchor_at.x, -origin_y,
                self.width, canvas_height,
                border_color=self.wire_color,
                border_width=self.wire_width,
                scale=self.quality_scale
            )

            """
            ctx = cairo.Context(inv_canvas)
            ctx.translate(self.anchor_at.x, origin_y)
            ctx.rectangle(-25, -25, 50, 50)
            draw_stroke(ctx, 4, "000000")
            """

            final_canvas = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(self.width), int(self.height))
            ctx  = cairo.Context(final_canvas)

            """
            ctx.rectangle(0, 0, final_canvas.get_width(), final_canvas.get_height())
            draw_fill(ctx, "0000ff")
            """

            ctx.scale(1, -1)
            if ay<iay:
                ctx.translate(0, -self.height)
            else:
                ctx.translate(0, -2*origin_y)
            ctx.set_source_surface(inv_canvas)
            ctx.get_source().set_filter(cairo.FILTER_FAST)
            ctx.paint()

            del ctx
            self.image_canvas = final_canvas
            del inv_canvas

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
                self.build_image()
            self.image_hash = image_hash
        elif self.image_canvas is None or \
             self.should_rebuild_d3 or \
             self.should_rebuild_camera or \
             self.should_rebuild_image:
            self.build_image()
        ctx.restore()

        ctx.save()
        if self.high_quality:
            mat = ctx.get_matrix()
            ctx.set_matrix(cairo.Matrix())
            rect = self.get_abs_reverse_outline(0, 0, self.width, self.height)
            ctx.translate(rect.left, rect.top)
            ctx.set_source_surface(self.image_canvas)
            ctx.set_matrix(mat)
            self.draw_path(ctx)
            ctx.clip()
            ctx.paint()
            ctx.set_matrix(mat)
        else:
            ctx.set_source_surface(self.image_canvas)
            ctx.get_source().set_filter(cairo.FILTER_FAST)
            ctx.paint()
        ctx.restore()
