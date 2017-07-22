from shape import Shape
from ..commons import Rect, copy_value, draw_fill, draw_stroke

class CurveJoinerShape(Shape):
    TYPE_NAME = "curve_joiner"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height):
        Shape.__init__(self, anchor_at, border_color, border_width, fill_color, width, width)
        self.curve_shape_1 = None
        self.curve_shape_2 = None

    @classmethod
    def get_pose_prop_names(cls):
        return []

    def get_xml_element(self):
        elm = Shape.get_xml_element(self)
        if self.curve_shape_1:
            elm.attrib["c1"] = self.curve_shape_1.get_name()
        if self.curve_shape_2:
            elm.attrib["c2"] = self.curve_shape_2.get_name()
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        arr = Shape.get_params_array_from_xml_element(elm)
        shape = cls(*arr)
        shape.assign_params_from_xml_element(elm)
        return shape

    def copy(self, copy_name=False, deep_copy=False):
        newob = CurveJoinerShape(
                        self.anchor_at.copy(),
                        copy_value(self.border_color), self.border_width, copy_value(self.fill_color),
                        self.width, self.height)
        self.copy_into(newob, copy_name, all_fields=deep_copy)
        return newob

    def get_curve_1(self):
        if self.curve_shape_1:
            return self.curve_shape_1.get_name()
        return "1"

    def get_curve_2(self):
        if self.curve_shape_2:
            return self.curve_shape_2.get_name()
        return ""

    def set_curve_1(self, value):
        self.curve_shape_1 = self.parent_shape.get_interior_shape(value)

    def set_curve_2(self, value):
        self.curve_shape_2 = self.parent_shape.get_interior_shape(value)

    def draw(self, ctx, fixed_border=True, root_shape=None):
        paths = []
        if self.curve_shape_1:
            ctx.save()
            self.curve_shape_1.pre_draw(ctx, root_shape=root_shape)
            self.curve_shape_1.draw_path(ctx, for_fill=True)
            ctx.restore()
            paths.append(ctx.copy_path())

        if self.curve_shape_2:
            ctx.save()
            self.curve_shape_2.pre_draw(ctx, root_shape=root_shape)
            origin = self.curve_shape_2.curves[0].origin
            ctx.line_to(origin.x, origin.y)
            self.curve_shape_2.draw_path(ctx, for_fill=True)
            ctx.restore()
            ctx.save()
            self.curve_shape_1.pre_draw(ctx, root_shape=root_shape)
            origin = self.curve_shape_1.curves[0].origin
            ctx.line_to(origin.x, origin.y)
            ctx.restore()
            paths.append(ctx.copy_path())


        if self.fill_color:
            ctx.save()
            ctx.new_path()
            for path in paths:
                ctx.append_path(path)
            ctx.close_path()
            ctx.restore()
            draw_fill(ctx, self.fill_color)

        if self.border_width>0 and self.border_color:
            ctx.save()
            ctx.new_path()
            for path in paths:
                ctx.append_path(path)
            ctx.restore()
            draw_stroke(ctx, self.border_width, self.border_color)

    def get_outline(self, padding):
        return Rect(-padding, -padding, self.width+2*padding, self.height+2*padding, 0)

