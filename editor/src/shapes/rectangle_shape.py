from ..commons import *
from shape import Shape

class RectangleShape(Shape):
    TYPE_NAME = "rectangle"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius):
        Shape.__init__(self, anchor_at, border_color, border_width, fill_color, width, height)
        self.corner_radius = corner_radius

    @classmethod
    def get_pose_prop_names(cls):
        prop_names = Shape.get_pose_prop_names()
        prop_names.append("corner_radius")
        return prop_names

    def get_xml_element(self):
        elm = Shape.get_xml_element(self)
        elm.attrib["corner_radius"] = "{0}".format(self.corner_radius)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        arr = Shape.get_params_array_from_xml_element(elm)
        corner_radius_str = elm.attrib.get("corner_radius", "0")
        arr.append(float(corner_radius_str))
        shape = cls(*arr)
        shape.assign_params_from_xml_element(elm)
        return shape

    def copy(self, copy_name=False, deep_copy=False):
        newob = RectangleShape(self.anchor_at.copy(), copy_value(self.border_color), self.border_width,
                        copy_value(self.fill_color), self.width, self.height, self.corner_radius)
        self.copy_into(newob, copy_name, all_fields=deep_copy)
        return newob

    def draw_path(self, ctx, for_fill=False):
        if not for_fill and not self.border_color:
            return
        if for_fill and not self.fill_color:
            return
        draw_rounded_rectangle(ctx, 0, 0, self.width, self.height, self.corner_radius)

    def get_outline(self, padding):
        return Rect(-padding, -padding, self.width+2*padding, self.height+2*padding, self.corner_radius+padding)

    def get_corner_radius(self):
        return self.corner_radius

    def set_corner_radius(self, value):
        self.corner_radius = value
