from point import Point
from rect import Rect
from xml.etree.ElementTree import Element as XmlElement
import numpy, math

class Polygon(object):
    TAG_NAME = "polygon"

    def __init__(self, points=None, closed=False):
        self.points = []
        if points is not None:
            self.points.extend(points)
        self.closed = closed

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["closed"] = "{0}".format(self.closed)
        for point in self.points:
            elm.append(point.get_xml_element())
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        closed = (elm.attrib["closed"] == "True")
        polygon = cls(closed=closed)
        for point_element in elm.findall(Point.TAG_NAME):
            polygon.points.append(Point.create_from_xml_element(point_element))
        return polygon

    def copy(self):
        newob = Polygon(closed=self.closed)
        for point in self.points:
            newob.add_point(point.copy())
        return newob

    def add_point(self, point):
        self.points.append(point)

    def remove_point(self, point):
        self.points.remove(point)

    def set_closed(self, closed):
        self.closed = closed

    def get_outline(self):
        outline = None
        for i in range(len(self.points)):
            if i<1: continue
            x1 = self.points[i-1].x
            x2 = self.points[i].x

            y1 = self.points[i-1].y
            y2 = self.points[i].y

            rect = Rect(left=min(x1, x2), top=min(y1, y2), width=abs(x2-x1), height=abs(y2-y1))
            if outline is None:
                outline = rect
            else:
                outline.expand_include(rect)
        return outline

    def translate(self, dx, dy):
        for point in self.points:
            point.translate(dx, dy)

    def scale(self, sx ,sy):
        for point in self.points:
            point.scale(sx, sy)

    def draw_path(self, ctx):
        ctx.new_path()
        for pi in range(len(self.points)):
            point = self.points[pi]
            if pi == 0:
                ctx.move_to(point.x, point.y)
            else:
                ctx.line_to(point.x, point.y)
        if self.closed:
            ctx.close_path()

    @staticmethod
    def get_reals(roots):
        mod_roots = []
        for root in roots:
            if root>=1. or root<=0: continue
            mod_roots.append(root)
        return mod_roots

    def get_closest_point(self, point, width, height):
        points_count = len(self.points)
        if not self.closed:
            points_count -= 1
        for point_index in range(points_count):
            p0 = self.points[point_index]
            p1 = self.points[(point_index+1)%len(self.points)]

            x_coeff = [(p1.x-p0.x)*width, (p0.x-point.x)*width]
            y_coeff = [(p1.y-p0.y)*height, (p0.y-point.y)*height]

            for i in range(len(x_coeff)):
                if abs(x_coeff[i])<1: x_coeff[i] = 0
            for i in range(len(y_coeff)):
                if abs(y_coeff[i])<1: y_coeff[i] = 0

            x_roots = numpy.roots(x_coeff)
            y_roots = numpy.roots(y_coeff)

            mod_x_roots = self.get_reals(x_roots)
            mod_y_roots = self.get_reals(y_roots)

            if not x_roots and mod_y_roots and x_coeff[0]==0 and abs(x_coeff[1])<5:#horizontal
                return point_index, mod_y_roots[0]
            if not y_roots and mod_x_roots and y_coeff[0]==0 and abs(y_coeff[1])<5:#vertical
                return point_index, mod_x_roots[0]

            for x_root in mod_x_roots:
                for y_root in mod_y_roots:
                    if abs(x_root-y_root)<5:
                        return point_indxex, x_root
                        break
        return None

    def insert_point_at(self, point_index, t):
        if point_index>=len(self.points): return False
        if not self.closed and point_index>=len(self.points)-1: return False

        p0 = self.points[point_index]
        p1 = self.points[(point_index+1)%len(self.points)]

        tx = p0.x + (p1.x-p0.x)*t
        ty = p0.y + (p1.y-p0.y)*t

        self.points.insert(point_index+1, Point(tx, ty))
        return True
