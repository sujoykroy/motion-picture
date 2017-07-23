from shape import Shape
from ..commons import Rect, copy_value, draw_fill, draw_stroke

class JoinerItem(object):
    def __init__(self, joiner_shape, curve_name):
        if curve_name[0] == "-":
            self.reversed = True
            self.curve_name = curve_name[1:]
        else:
            self.reversed = False
            self.curve_name = curve_name
        self.curve_shape = joiner_shape.parent_shape.get_interior_shape(self.curve_name)

    def draw_path(self, ctx, join, root_shape):
       if self.curve_shape:
            ctx.save()
            self.curve_shape.pre_draw(ctx, root_shape=root_shape)
            ctx.scale(self.curve_shape.width, self.curve_shape.height)
            curve = self.curve_shape.curves[0]
            if self.reversed:
                if join:
                    start_point = curve.bezier_points[-1].dest
                    ctx.line_to(start_point.x, start_point.y)
                curve.reverse_draw_path(ctx)
            else:
                if join:
                    start_point = curve.origin
                    ctx.line_to(start_point.x, start_point.y)
                curve.draw_path(ctx, new_path=False)
            ctx.restore()

class CurveJoinerShape(Shape):
    TYPE_NAME = "curve_joiner"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height):
        Shape.__init__(self, anchor_at, border_color, border_width, fill_color, width, width)
        self.joiner_items = []
        self.joined_names = ""

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

    def set_joined_names(self, value):
        self.joined_names = value
        del self.joiner_items[:]
        for name in value.split(","):
            name = name.strip()
            if not name:
                continue
            self.joiner_items.append(JoinerItem(self, name))

    def draw(self, ctx, fixed_border=True, root_shape=None):
        ctx.new_path()
        join = False
        for joiner_item in self.joiner_items:
            joiner_item.draw_path(ctx, join, root_shape)
            join = True
        path = ctx.copy_path()

        if self.fill_color:
            ctx.save()
            ctx.new_path()
            ctx.append_path(path)
            ctx.restore()
            draw_fill(ctx, self.fill_color)

        if self.border_width>0 and self.border_color:
            ctx.save()
            ctx.new_path()
            ctx.append_path(path)
            ctx.restore()
            draw_stroke(ctx, self.border_width, self.border_color)

    def get_outline(self, padding):
        return Rect(-padding, -padding, self.width+2*padding, self.height+2*padding, 0)

