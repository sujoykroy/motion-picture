from bezier_point import BezierPoint
from point import Point
from xml.etree.ElementTree import Element as XmlElement

class Curve(object):
    TAG_NAME = "curve"

    def __init__(self, origin, bezier_points=None, closed=False):
        self.origin = origin
        self.bezier_points = []
        if bezier_points is not None:
            self.bezier_points.extend(bezier_points)
        self.closed = closed

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["origin"] = self.origin.to_text()
        elm.attrib["closed"] = "{0}".format(self.closed)
        for bezier_point in self.bezier_points:
            elm.append(bezier_point.get_xml_element())
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        origin = Point.from_text(elm.attrib["origin"])
        closed = (elm.attrib["closed"] == "True")
        curve = cls(origin=origin, closed=closed)
        for bezier_point_element in elm.findall(BezierPoint.TAG_NAME):
            curve.bezier_points.append(BezierPoint.create_from_xml_element(bezier_point_element))
        return curve

    def copy(self):
        newob = Curve(self.origin.copy(), closed=self.closed)
        for bezier_point in self.bezier_points:
            newob.add_bezier_point(bezier_point.copy())
        return newob

    def add_bezier_point(self, bezier_point):
        self.bezier_points.append(bezier_point)

    def remove_bezier_point(self, bezier_point):
        self.bezier_points.remove(bezier_point)

    def set_closed(self, closed):
        self.closed = closed

    def get_outline(self):
        outline = None
        for bz in self.bezier_points:
            if outline is None:
                outline = bz.get_outline()
            else:
                outline.expand_include(bz.get_outline())
        if outline is None: return
        if self.origin.x<outline.left:
            dx = outline.left - self.origin.x
            outline.left = self.origin.x
            outline.width += dx
        elif self.origin.x>outline.left+outline.width:
            dx = self.origin.x - outline.left-outline.width
            outline.width += dx

        if self.origin.y<outline.top:
            dy = outline.top - self.origin.y
            outline.top = self.origin.y
            outline.height += dy
        elif self.origin.y>outline.top+outline.height:
            dy = self.origin.y - outline.top - outline.height
            outline.height += dy

        return outline

    def translate(self, dx, dy):
        self.origin.translate(dx, dy)
        for bezier_point in self.bezier_points:
            bezier_point.translate(dx, dy)

    def scale(self, sx ,sy):
        self.origin.scale(sx, sy)
        for bezier_point in self.bezier_points:
            bezier_point.scale(sx, sy)

    def draw_path(self, ctx):
        ctx.move_to(self.origin.x, self.origin.y)
        for bezier_point in self.bezier_points:
            ctx.curve_to(
                bezier_point.control_1.x, bezier_point.control_1.y,
                bezier_point.control_2.x, bezier_point.control_2.y,
                bezier_point.dest.x, bezier_point.dest.y)
        if len(self.bezier_points) > 1 and self.closed:
            ctx.close_path()

class StraightCurve(Curve):
    def __init__(self, points):
        Curve.__init__(self, points[0])
        for point in points[1:]:
            self.add_bezier_point(BezierPoint(point, point, point))
