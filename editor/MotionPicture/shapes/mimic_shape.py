from .shape import Shape
from xml.etree.ElementTree import Element as XmlElement
from ..commons import Point

class MimicShape(Shape):
    TYPE_NAME = "mimic"

    def __init__(self, mimic_like):
        super(MimicShape, self).__init__(Point(0,0), None, 0., None, 0., 0.)
        self.mimic_like = mimic_like
        self.mimic_like_shape = None
        self.selectable = False
        self.has_outline = False

    def set_mimic_like(self, value):
        if isinstance(value, str):
            value = value.decode("utf-8")
        self.mimic_like = value
        self.mimic_like_shape = self.parent_shape.get_interior_shape(self.mimic_like)

    def get_mimic_like(self):
        if self.mimic_like_shape:
            return self.mimic_like_shape.get_shape_path(root_shape=self.parent_shape)
        return ""

    def build_mimic_like_shape(self):
        self.set_mimic_like(self.mimic_like)

    def set_locked_to(self, value, direct=False):
        pass

    def get_locked_to(self):
        return ""

    @classmethod
    def get_pose_prop_names(cls):
        return ["visible"]

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["type"] = self.TYPE_NAME
        elm.attrib["name"] = self.get_name()
        if not self.visible:
            elm.attrib["visible"] = "0"
        elm.attrib["mimic_like"] = u"{0}".format(self.mimic_like)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        shape = MimicShape(mimic_like=elm.attrib.get("mimic_like"))
        shape.rename(elm.attrib.get("name"))
        shape.visible = bool(int(elm.attrib.get("visible", 1)))
        return shape

    def copy(self, copy_name=False, deep_copy=False):
        newob = MimicShape(mimic_like=self.mimic_like)
        return newob
