from .shape import Shape
from ..commons import Rect, copy_value, draw_fill, draw_stroke, draw_oval
from ..commons import Text, CurvePoint
import math
from .curve_shape import CurveShape

class JoinerItem(object):
    def __init__(self, joiner_shape, curve_name):
        if curve_name[0] == "-":
            self.reversed = True
            self.curve_name = curve_name[1:]
        else:
            self.reversed = False
            self.curve_name = curve_name
        arr = self.curve_name.split("/")
        if len(arr)>1:
            self.curve_index = int(Text.parse_number(arr[1], 0))
            self.curve_name = arr[0]
        else:
            self.curve_index = 0
        shape = joiner_shape.parent_shape.get_interior_shape(self.curve_name)
        if not isinstance(shape, CurveShape):
            shape = None
        self.curve_shape = shape

    def draw_path(self, ctx, join, root_shape):
       if self.curve_shape:
            ctx.save()
            self.curve_shape.pre_draw(ctx, root_shape=root_shape)
            self.curve_shape.draw_curve(ctx,
                        curve_index=self.curve_index,
                        line_to=join, reverse=self.reversed, new_path=False)
            ctx.restore()

    def draw_start_end(self, ctx, root_shape):
       if self.curve_shape and self.curve_index<len(self.curve_shape.curves):
            curve = self.curve_shape.curves[self.curve_index]
            start_curve_point = CurvePoint(
                self.curve_index, len(curve.bezier_points)-1, CurvePoint.POINT_TYPE_DEST)
            end_curve_point = CurvePoint(
                self.curve_index, -1, CurvePoint.POINT_TYPE_ORIGIN)
            start_point = self.curve_shape.get_point_location(start_curve_point)
            end_point = self.curve_shape.get_point_location(end_curve_point)

            if self.reversed:
                start_point, end_point = end_point, start_point

            params = [[start_point, "70ede3", "ff0000"], [end_point, "ea3a84", "00ff00"]]
            for point, fill_color, border_color in params:
                for i in range(2):
                    ctx.save()
                    ctx.new_path()
                    self.curve_shape.pre_draw(ctx, root_shape=root_shape)
                    #ctx.scale(self.curve_shape.width, self.curve_shape.height)
                    ctx.translate(point.x, point.y)
                    ctx.scale(10, 10)
                    ctx.move_to(.5,0)
                    ctx.arc(0,0,.5,0, 2*math.pi)
                    ctx.close_path()
                    ctx.restore()
                    if i == 0:
                        draw_fill(ctx, fill_color)
                    else:
                        draw_stroke(ctx, 2, border_color)

    def complete(self, ctx, root_shape):
        if self.curve_shape:
            ctx.save()
            self.curve_shape.pre_draw(ctx, root_shape=root_shape)
            curve = self.curve_shape.curves[self.curve_index]
            if self.reversed:
                curve_point = CurvePoint(
                    self.curve_index, len(curve.bezier_points)-1, CurvePoint.POINT_TYPE_DEST)
            else:
                curve_point = CurvePoint(
                    self.curve_index, -1, CurvePoint.POINT_TYPE_ORIGIN)
            start_point = self.curve_shape.get_point_location(curve_point)
            ctx.line_to(start_point.x, start_point.y)
            ctx.restore()

class CurveJoinerShape(Shape):
    TYPE_NAME = "curve_joiner"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height):
        Shape.__init__(self, anchor_at, border_color, border_width, fill_color, width, width)
        self.joiner_items = []
        self.joined_names = ""
        self.show_ends = False
        self.has_outline = False

    @classmethod
    def get_pose_prop_names(cls):
        return ["border_color", "border_width", "fill_color"]

    def get_xml_element(self):
        elm = Shape.get_xml_element(self)
        elm.attrib["joined_names"] = u"{0}".format(self.joined_names)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        arr = Shape.get_params_array_from_xml_element(elm)
        shape = cls(*arr)
        shape.assign_params_from_xml_element(elm)
        shape.joined_names = elm.attrib.get("joined_names")
        return shape

    def copy(self, copy_name=False, deep_copy=False):
        newob = CurveJoinerShape(
                        self.anchor_at.copy(),
                        copy_value(self.border_color), self.border_width,
                        copy_value(self.fill_color),
                        self.width, self.height)
        self.copy_into(newob, copy_name, all_fields=deep_copy)
        newob.joined_names = self.joined_names
        return newob

    def build_joiner_items(self):
        self.set_joined_names(self.joined_names)

    def set_joined_names(self, value):
        if isinstance(value, str):
            value = value.decode("utf-8")
        self.joined_names = value
        del self.joiner_items[:]
        for name in value.split(","):
            name = name.strip()
            if not name:
                continue
            self.joiner_items.append(JoinerItem(self, name))

    def draw(self, ctx, fixed_border=True, root_shape=None):
        if not self.joiner_items:
            return
        ctx.new_path()
        join = False
        for joiner_item in self.joiner_items:
            joiner_item.draw_path(ctx, join, root_shape)
            join = True
        if len(self.joiner_items)>1:
            self.joiner_items[0].complete(ctx, root_shape)
        path = ctx.copy_path()

        if self.fill_color:
            ctx.save()
            ctx.new_path()
            ctx.append_path(path)
            ctx.restore()
            draw_fill(ctx, self.fill_color, even_odd=False)

        if self.border_width>0 and self.border_color:
            ctx.save()
            ctx.new_path()
            ctx.append_path(path)
            ctx.restore()
            draw_stroke(ctx, self.border_width, self.border_color)

        if self.show_ends:
            for joiner_item in self.joiner_items:
                joiner_item.draw_start_end(ctx, root_shape)

    def get_outline(self, padding):
        return Rect(0, 0, 0, 0)

    def get_abs_outline(self, padding):
        return Rect(0, 0, 0, 0)

