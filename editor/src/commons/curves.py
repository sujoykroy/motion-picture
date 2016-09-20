from bezier_point import BezierPoint
from point import Point
from xml.etree.ElementTree import Element as XmlElement
import numpy, math

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

    def reverse_copy(self):
        newob = Curve(self.bezier_points[-1].dest.copy(), closed=self.closed)
        for i in range(len(self.bezier_points)-1, -1, -1):
            bzp = self.bezier_points[i]
            if i == 0:
                next_dest = self.origin
            else:
                next_dest = self.bezier_points[i-1].dest
            newob.add_bezier_point(BezierPoint(
                control_1=bzp.control_2.copy(),
                control_2=bzp.control_1.copy(),
                dest = next_dest.copy()))
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


    @staticmethod
    def get_reals(roots):
        mod_roots = []
        for root in roots:
            if isinstance(root, numpy.complex128):
                root = root.real
            if root>=1. or root<=0: continue
            mod_roots.append(root)
        return mod_roots

    def get_closest_control_point(self, point, width, height):
        last_dest = self.origin
        for bezier_point_index in range(len(self.bezier_points)):
            bezier_point = self.bezier_points[bezier_point_index]

            p0 = last_dest
            p1 = bezier_point.control_1
            p2 = bezier_point.control_2
            p3 = bezier_point.dest
            last_dest = p3

            x_coeff = [(-p0.x+3*p1.x-3*p2.x+p3.x), (3*p0.x-6*p1.x+3*p2.x),
                       (-3*p0.x+3*p1.x), p0.x-point.x]
            y_coeff = [(-p0.y+3*p1.y-3*p2.y+p3.y), (3*p0.y-6*p1.y+3*p2.y),
                       (-3*p0.y+3*p1.y), p0.y-point.y]

            for i in range(len(x_coeff)):
                x_coeff[i] *= width
                if abs(x_coeff[i])<5: x_coeff[i] = 0
            for i in range(len(y_coeff)):
                y_coeff[i] *= height
                if abs(y_coeff[i])<5: y_coeff[i] = 0

            x_roots = numpy.roots(x_coeff)
            y_roots = numpy.roots(y_coeff)

            mod_x_roots = self.get_reals(x_roots)
            mod_y_roots = self.get_reals(y_roots)

            x_roots = mod_x_roots
            y_roots = mod_y_roots

            if not x_roots and mod_y_roots and any((cf==0 for cf in x_coeff)) \
                           and abs(x_coeff[-1])<5:#horizontal
                return bezier_point_index, mod_y_roots[0]
            if not y_roots and mod_x_roots and any((cf==0 for cf in y_coeff)) \
                           and abs(y_coeff[-1])<5:#vertical
                return bezier_point_index, mod_x_roots[0]

            for x_root in x_roots:
                for y_root in y_roots:
                    if abs((x_root-y_root)/x_root)<.1:
                        return bezier_point_index, x_root
                        break
        return None

    def insert_point_at(self, bezier_point_index, t):
        if bezier_point_index>=len(self.bezier_points): return
        bezier_point = self.bezier_points[bezier_point_index]
        if bezier_point_index == 0:
            p0 = self.origin
        else:
            p0 = self.bezier_points[bezier_point_index-1].dest
        p1 = bezier_point.control_1
        p2 = bezier_point.control_2
        p3 = bezier_point.dest

        tm1 = 1-t

        p0p1_x = tm1*p0.x + t*p1.x
        p0p1_y = tm1*p0.y + t*p1.y

        p1p2_x = tm1*p1.x + t*p2.x
        p1p2_y = tm1*p1.y + t*p2.y

        p2p3_x = tm1*p2.x + t*p3.x
        p2p3_y = tm1*p2.y + t*p3.y

        p0p1_p1p2_x = tm1*p0p1_x + t*p1p2_x
        p0p1_p1p2_y = tm1*p0p1_y + t*p1p2_y

        p1p2_p2p3_x = tm1*p1p2_x + t*p2p3_x
        p1p2_p2p3_y = tm1*p1p2_y + t*p2p3_y

        tx = tm1*p0p1_p1p2_x + t*p1p2_p2p3_x
        ty = tm1*p0p1_p1p2_y + t*p1p2_p2p3_y

        post_bzp = BezierPoint(
            control_1 = Point(p1p2_p2p3_x, p1p2_p2p3_y),
            control_2 = Point(p2p3_x, p2p3_y),
            dest=bezier_point.dest.copy()
        )

        bezier_point.control_1.x = p0p1_x
        bezier_point.control_1.y = p0p1_y
        bezier_point.control_2.x = p0p1_p1p2_x
        bezier_point.control_2.y = p0p1_p1p2_y
        bezier_point.dest.x = tx
        bezier_point.dest.y = ty

        if bezier_point_index == len(self.bezier_points)-1:
            self.bezier_points.append(post_bzp)
        else:
            self.bezier_points.insert(bezier_point_index+1, post_bzp)

    @staticmethod
    def move_point_forward(point, base_point, to_point):
        rel_point = point.diff(base_point)
        to_distance = to_point.distance(base_point)
        angle = rel_point.get_angle()*math.pi/180.
        dx = to_distance*math.cos(angle)
        dy = to_distance*math.sin(angle)
        final_point = Point(base_point.x+dx, base_point.y + dy)
        return final_point

    def _get_avg_point(self, *points):
        x = 0.
        y = 0.
        for point in points:
            x += point.x
            y += point.y
        return Point(x/len(points), y/len(points))

    def smoothe_out(self, task_start, task_end):
        i = 1
        while i<len(self.bezier_points):
            prev_bzp = self.bezier_points[i-1]
            cur_bzp = self.bezier_points[i]
            if i > 1:
                base = self.bezier_points[i-2].dest
                ances_bzp = self.bezier_points[i-2]
                mid_point = self._get_avg_point(
                    ances_bzp.control_1, ances_bzp.control_2,
                    cur_bzp.control_1, cur_bzp.control_2
                )
            else:
                base = self.origin
                mid_point = Point(
                    (base.x+prev_bzp.dest.x+cur_bzp.dest.x)/3.,
                    (base.y+prev_bzp.dest.y+cur_bzp.dest.y)/3.
                )
            prev_slope_point = prev_bzp.dest.diff(base)
            post_slope_point = cur_bzp.control_1.diff(base)
            pre_angle = prev_slope_point.get_angle()
            post_angle = post_slope_point.get_angle()
            if abs(post_angle-pre_angle)<1:
                task = task_start()

                cur_bzp.control_1.copy_from(self.move_point_forward(prev_bzp.control_1, base, mid_point))
                cur_bzp.control_2.copy_from(self.move_point_forward(cur_bzp.control_2, cur_bzp.dest, mid_point))
                del self.bezier_points[i-1]
                task_end(task)
            else:
                base = prev_bzp.dest.copy()
                i += 1
