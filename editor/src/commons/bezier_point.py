from xml.etree.ElementTree import Element as XmlElement
from rect import Rect

class BezierPoint(object):
    TAG_NAME = "bp"

    def __init__(self, control_1, control_2, dest):
        self.control_1 = control_1
        self.control_2 = control_2
        self.dest = dest

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["c1"] =self.control_1.to_text()
        elm.attrib["c2"] = self.control_2.to_text()
        elm.attrib["d"] = self.dest.to_text()
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        control_1 = Point.from_text(elm.attrib["c1"])
        control_2 = Point.from_text(elm.attrib["c2"])
        dest = Point.from_text(elm.attrib["d"])
        bezier_point = cls(control_1=control_1, control_2=control_2, dest=dest)
        return bezier_point

    def copy(self):
        return BezierPoint(self.control_1.copy(), self.control_2.copy(), self.dest.copy())

    def get_outline(self):
        left = right = self.control_1.x
        top = bottom = self.control_1.y

        if left>self.control_2.x: left = self.control_2.x
        if right<self.control_2.x: right = self.control_2.x
        if top>self.control_2.y: top = self.control_2.y
        if bottom<self.control_2.y: bottom = self.control_2.y

        if left>self.dest.x: left = self.dest.x
        if right<self.dest.x: right = self.dest.x
        if top>self.dest.y: top = self.dest.y
        if bottom<self.dest.y: bottom = self.dest.y

        return Rect(left, top, right-left, bottom-top)

    def translate(self, dx, dy):
        self.control_1.translate(dx ,dy)
        self.control_2.translate(dx ,dy)
        self.dest.translate(dx ,dy)

    def scale(self, sx, sy):
        self.control_1.scale(sx ,sy)
        self.control_2.scale(sx ,sy)
        self.dest.scale(sx ,sy)
