from xml.etree.ElementTree import Element as XmlElement
from shape import Shape
from ..commons import Curve

class CurvesForm(object):
    TAG_NAME = "form"

    def __init__(self, width, height, curves, shapes_props=None, name=None):
        self.width = width
        self.height = height
        self.curves = curves
        self.name = name
        self.shapes_props= shapes_props

    def copy(self):
        curves = []
        for curve in self.curves:
            curves.append(curve.copy())
        newob = CurvesForm(self.width, self.height, self.curves, self.shapes_props, self.name)
        return newob

    def set_name(self, name):
        self.name = name

    def get_xml_element(self):
        form_elm = XmlElement(self.TAG_NAME)
        if self.name:
            form_elm.attrib["name"] = self.name
        form_elm.attrib["width"] = "{0}".format(self.width)
        form_elm.attrib["height"] = "{0}".format(self.height)
        for curve in self.curves:
            form_elm.append(curve.get_xml_element())
        if self.shapes_props:
            for shape_name, prop_dict in self.shapes_props.items():
                pose_shape_elm = Shape.get_pose_prop_xml_element(shape_name, prop_dict)
                form_elm.append(pose_shape_elm)
        return form_elm

    @classmethod
    def create_from_xml_element(cls, elm):
        name = elm.attrib.get("name", None)
        width = float(elm.attrib["width"])
        height = float(elm.attrib["height"])
        curves = []
        for curve_elm in elm.findall(Curve.TAG_NAME):
            curves.append(Curve.create_from_xml_element(curve_elm))

        shapes_props = None
        for pose_shape_elm in elm.findall(Shape.POSE_SHAPE_TAG_NAME):
            shape_name, prop_dict = Shape.create_pose_prop_dict_from_xml_element(pose_shape_elm)
            if shapes_props is None:
                shapes_props = dict()
            shapes_props[shape_name] = prop_dict
        return CurvesForm(name=name, width=width, height=height,
                          curves=curves, shapes_props=shapes_props)
