from ..commons import *
from shape import Shape
from oval_shape import OvalShape

class RingShape(OvalShape):
    TYPE_NAME = "ring"

    def __init__(self, anchor_at, border_color, border_width, fill_color,
                       width, height, sweep_angle, thickness):
        OvalShape.__init__(self, anchor_at, border_color, border_width, fill_color,
                                 width, height, sweep_angle)
        self.thickness = thickness
        self.curve= None
        self._update_path()

    @classmethod
    def get_pose_prop_names(cls):
        prop_names = OvalShape.get_pose_prop_names()
        prop_names.append("thickness")
        return prop_names

    def get_xml_element(self):
        elm = OvalShape.get_xml_element(self)
        elm.attrib["thickness"] = "{0}".format(self.thickness)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        arr = Shape.get_params_array_from_xml_element(elm)
        arr.append(float(elm.attrib.get("sweep_angle", 360)))
        arr.append(float(elm.attrib.get("thickness", 0)))
        shape = cls(*arr)
        shape.assign_params_from_xml_element(elm)
        return shape

    def copy(self, copy_name=False, deep_copy=False):
        newob = RingShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                            self.fill_color.copy(), self.width, self.height,
                            self.sweep_angle, self.thickness)
        self.copy_into(newob, copy_name)
        return newob

    def _update_path(self):
        self.curve = Curve.create_ring(self.sweep_angle, self.thickness)

    def set_sweep_angle(self, sweep_angle):
        self.sweep_angle = sweep_angle
        self._update_path()

    def set_thickness(self, thickness):
        self.thickness = thickness
        self._update_path()

    def draw_path(self, ctx, for_fill=False):
        ctx.new_path()
        ctx.save()
        ctx.scale(self.width, self.height)
        self.curve.draw_path(ctx)
        ctx.restore()


