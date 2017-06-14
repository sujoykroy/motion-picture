from ..commons import *
from shape import Shape

class OvalShape(Shape):
    TYPE_NAME = "oval"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, sweep_angle):
        Shape.__init__(self, anchor_at, border_color, border_width, fill_color, width, height)
        self.sweep_angle = sweep_angle

    @classmethod
    def get_pose_prop_names(cls):
        prop_names = Shape.get_pose_prop_names()
        prop_names.append("sweep_angle")
        return prop_names

    def get_xml_element(self):
        elm = Shape.get_xml_element(self)
        elm.attrib["sweep_angle"] = "{0}".format(self.sweep_angle)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        arr = Shape.get_params_array_from_xml_element(elm)
        sweep_angle_str = elm.attrib.get("sweep_angle", "360")
        arr.append(float(sweep_angle_str))
        shape = cls(*arr)
        shape.assign_params_from_xml_element(elm)
        return shape

    def copy(self, copy_name=False, deep_copy=False):
        newob = OvalShape(self.anchor_at.copy(), copy_value(self.border_color), self.border_width,
                          copy_value(self.fill_color), self.width, self.height, self.sweep_angle)
        self.copy_into(newob, copy_name)
        return newob

    def draw_path(self, ctx, for_fill=False):
        draw_oval(self, ctx, self.width, self.height, self.sweep_angle)

    def is_within(self, point):
        point = self.transform_point(point)
        dx = (point.x-self.width*.5)/(self.width*.5)
        dy = (point.y-self.height*.5)/(self.height*.5)
        return dx*dx+dy*dy<=1

    def get_sweep_angle(self):
        return self.sweep_angle

    def set_sweep_angle(self, value):
        self.sweep_angle = value

