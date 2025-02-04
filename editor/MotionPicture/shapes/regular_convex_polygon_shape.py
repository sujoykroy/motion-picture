from ..commons import *
from .shape import Shape

class RegularConvexPolygonShape(Shape):
    TYPE_NAME = "regular_convex_polygon"


    @classmethod
    def create_blank(cls, width, height):
        return cls(Point(width*.5, height*.5), None, 0, None, width, height, 0)

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, edges=6):
        Shape.__init__(self, anchor_at, border_color, border_width, fill_color, width, height)
        self.edges = edges


    @classmethod
    def get_pose_prop_names(cls):
        prop_names = Shape.get_pose_prop_names()
        prop_names.append("edges")
        return prop_names

    def get_xml_element(self):
        elm = Shape.get_xml_element(self)
        elm.attrib["edges"] = "{0}".format(self.edges)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        arr = Shape.get_params_array_from_xml_element(elm)
        edges_str = elm.attrib.get("edges", "0")
        arr.append(float(edges_str))
        shape = cls(*arr)
        shape.assign_params_from_xml_element(elm)
        return shape

    def copy(self, copy_name=False, deep_copy=False):
        newob = RegularConvexPolygonShape(self.anchor_at.copy(), copy_value(self.border_color), self.border_width,
                        copy_value(self.fill_color), self.width, self.height, self.edges)
        self.copy_into(newob, copy_name, all_fields=deep_copy)
        return newob

    def draw_path(self, ctx, for_fill=False):
        if not for_fill and not self.border_color:
            return
        if for_fill and not self.fill_color:
            return
        draw_regular_convex_polygon(ctx, 0, 0, self.width, self.height, self.edges)

    def get_outline(self, padding):
        return Rect(-padding, -padding, self.width+2*padding, self.height+2*padding, 0)

    def get_edges(self):
        return self.edges

    def set_edges(self, value):
        self.edges = value
