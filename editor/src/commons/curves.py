from bezier_point import BezierPoint
from point import Point, RAD_PER_DEG
from xml.etree.ElementTree import Element as XmlElement
import numpy, math
from scipy.spatial import distance

class Curve(object):
    TAG_NAME = "curve"

    def __init__(self, origin, bezier_points=None, closed=False):
        self.origin = origin
        self.bezier_points = []
        #TODO
        # bare points are more easing the erasing of freely drawn curves.
        # for normal small curves, this element needs to be out of
        # operation. some checks necessary to implement it.
        self.bare_point_xys = numpy.array([(origin.x, origin.y)])
        if bezier_points is not None:
            self.add_bezier_points(bezier_points)
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
            curve.add_bezier_point(BezierPoint.create_from_xml_element(bezier_point_element))
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
        self.bare_point_xys=numpy.append(self.bare_point_xys, [(bezier_point.dest.x, bezier_point.dest.y)], axis=0)

    def add_bezier_points(self, bezier_points):
        for bezier_point in bezier_points:
            self.add_bezier_point(bezier_point)

    def insert_bezier_point(self, index, bezier_point):
        self.bezier_points.insert(index, bezier_point)
        self.bare_point_xys=numpy.insert(self.bare_point_xys, index+1,
                 [(bezier_point.dest.x, bezier_point.dest.y)], axis=0)

    def remove_bezier_point_index(self, index):
        if index<0:
            index += len(self.bezier_points)
        del self.bezier_points[index]
        self.bare_point_xys=numpy.delete(self.bare_point_xys, index, axis=0)

    def remove_bezier_point_indices(self, start_index, end_index):
        for i in range(end_index-1, start_index-1, -1):
            self.bare_point_xys=numpy.delete(self.bare_point_xys, i, axis=0)
            del self.bezier_points[i]

    def update_bezier_point_index(self, index):
        if index<0:
            index += len(self.bezier_points)
        bezier_point = self.bezier_points[index]
        self.bare_point_xys[index+1][0] = bezier_point.dest.x
        self.bare_point_xys[index+1][1] = bezier_point.dest.y

    def update_origin(self):
        self.bare_point_xys[0][0] = self.origin.x
        self.bare_point_xys[0][1] = self.origin.y

    def get_indices_within(self, center, radius):
        distances = distance.cdist(self.bare_point_xys, [(center.x, center.y)])
        return numpy.nonzero(distances<radius)[0]

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
        self.update_origin()
        for index in range(len(self.bezier_points)):
            self.bezier_points[index].translate(dx, dy)
            self.update_bezier_point_index(index)

    def scale(self, sx ,sy):
        self.origin.scale(sx, sy)
        self.update_origin()
        for index in range(len(self.bezier_points)):
            self.bezier_points[index].scale(sx, sy)
            self.update_bezier_point_index(index)

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
            self.add_bezier_point(post_bzp)
        else:
            self.bezier_points.insert(bezier_point_index+1, post_bzp)
            self.bare_point_xys=numpy.insert(self.bare_point_xys, bezier_point_index+1,
                    [(post_bzp.dest.x, post_bzp.dest.y)], axis=0)

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

    def smooth_out(self, angle=1., task_start=None, task_end=None):
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
            if abs(post_angle-pre_angle)<angle:
                if task_start:
                    task = task_start()

                cur_bzp.control_1.copy_from(self.move_point_forward(prev_bzp.control_1, base, mid_point))
                cur_bzp.control_2.copy_from(self.move_point_forward(
                    cur_bzp.control_2, cur_bzp.dest, mid_point))
                del self.bezier_points[i-1]
                if task_end:
                    task_end(task)
            else:
                base = prev_bzp.dest.copy()
                i += 1


    @classmethod
    def create_circle(cls, sweep_angle=None):
        k = .5522847498*.5#magic number
        bezier_points = [
            BezierPoint(control_1=Point(1., .5+k), control_2=Point(.5+k, 1.), dest=Point(.5, 1.)),
            BezierPoint(control_1=Point(.5-k, 1.), control_2=Point(0, .5+k), dest=Point(0., .5)),
            BezierPoint(control_1=Point(0., .5-k), control_2=Point(0.5-k, 0.), dest=Point(.5, 0.)),
            BezierPoint(control_1=Point(.5+k, 0), control_2=Point(1., .5-k), dest=Point(1., .5)),
        ]
        curve = Curve(origin=Point(1., .5), bezier_points=bezier_points, closed=True)
        if sweep_angle is not None:
            if sweep_angle>360:
                sweep_angle %= 360.
            if sweep_angle<0:
                sweep_angle = 360+sweep_angle
            if 0<=sweep_angle<90:
                i = 0
            elif 90<=sweep_angle<180:
                i = 1
            elif 180<=sweep_angle<270:
                i = 2
            elif 270<=sweep_angle<=360:
                i = 3
            curve.insert_point_at(i, (sweep_angle-i*90)/90.)
            del curve.bezier_points[i+1:]
            curve.closed = (sweep_angle == 360)
        return curve

    @classmethod
    def create_ring(cls, sweep_angle, thickness):
        outer_curve = Curve.create_circle(sweep_angle=sweep_angle)
        if thickness <= 0:
            return outer_curve

        if thickness >= 1.:
            center_bzp = BezierPoint(
                    control_1=Point(.5, .5), control_2=Point(.5, .5), dest=Point(.5, .5))
            center_bzp.align_straight_with(outer_curve.bezier_points[-1].dest)
            origin_bzp = BezierPoint(
                    control_1=outer_curve.origin.copy(),
                    control_2=outer_curve.origin.copy(),
                    dest=outer_curve.origin.copy())
            origin_bzp.align_straight_with(center_bzp.dest)
            outer_curve.add_bezier_point(center_bzp)
            outer_curve.add_bezier_point(origin_bzp)
            outer_curve.closed = True
            return outer_curve

        outer_curve = outer_curve.reverse_copy()
        inner_curve = Curve.create_circle(sweep_angle=sweep_angle)
        inner_curve.translate(-.5, -.5)
        inner_curve.scale(1-thickness, 1-thickness)
        inner_curve.translate(.5, .5)

        outer_curve_origin_bzp = BezierPoint(
                control_1=outer_curve.origin.copy(),
                control_2=outer_curve.origin.copy(),
                dest = outer_curve.origin.copy())
        outer_curve_origin_bzp.align_straight_with(inner_curve.bezier_points[-1].dest)
        inner_curve.add_bezier_point(outer_curve_origin_bzp)
        inner_curve.bezier_points.extend(outer_curve.bezier_points)

        inner_curve_origin_bzp = BezierPoint(
                control_1=inner_curve.origin.copy(),
                control_2=inner_curve.origin.copy(),
                dest = inner_curve.origin.copy())
        inner_curve_origin_bzp.align_straight_with(inner_curve.bezier_points[-1].dest)
        inner_curve.closed = True
        return inner_curve

class CurvePoint(object):
    TAG_NAME="curve_point"

    POINT_TYPE_CONTROL_1 = 0
    POINT_TYPE_CONTROL_2 = 1
    POINT_TYPE_DEST = -1
    POINT_TYPE_ORIGIN = -2

    def __init__(self, curve_index, point_index, point_type):
        self.curve_index = curve_index
        self.point_index = point_index
        self.point_type = point_type

    def get_point(self, curve):
        bezier_point = curve.bezier_points[self.point_index]
        if self.point_type == CurvePoint.POINT_TYPE_DEST:
            point = bezier_point.dest
        elif self.point_type == CurvePoint.POINT_TYPE_CONTROL_1:
            point = bezier_point.control_1
        elif self.point_type == CurvePoint.POINT_TYPE_CONTROL_2:
            point = bezier_point.control_2
        elif self.point_type == CurvePoint.POINT_TYPE_ORIGIN:
            point = curve.origin
        return point

    def __eq__(self, other):
        return (self.curve_index == other.curve_index and \
                self.point_index == other.point_index and \
                self.point_type == other.point_type)

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["ci"] = "{0}".format(self.curve_index)
        elm.attrib["pi"] = "{0}".format(self.point_index)
        elm.attrib["pt"] = "{0}".format(self.point_type)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        curve_index = int(elm.attrib.get("ci", -1))
        point_index = int(elm.attrib.get("pi", -1))
        point_type = int(elm.attrib.get("pt", -1))
        if curve_index<0 or point_index<0:
            return None
        return cls(curve_index, point_index, point_type)

class CurvePointGroup(object):
    TAG_NAME = "curve_point_group"

    def __init__(self):
        self.points = []
        self.point_indices = dict()
        self.abs_anchor_at = None

    def set_abs_anchor_x(self, x):
        if self.abs_anchor_at is None:
            self.abs_anchor_at = Point(0,0)
        self.abs_anchor_at.x = x

    def set_abs_anchor_y(self, y):
        if self.abs_anchor_at is None:
            self.abs_anchor_at = Point(0,0)
        self.abs_anchor_at.y = y

    def set_abs_anchor_at(self, x, y):
        if self.abs_anchor_at is None:
            self.abs_anchor_at = Point(0,0)
        self.abs_anchor_at.x = x
        self.abs_anchor_at.y = y

    def add_point(self, curve_point):
        self.points.append(curve_point)
        if curve_point.curve_index not in self.point_indices:
            self.point_indices[curve_point.curve_index] = dict()
        self.point_indices[curve_point.curve_index][curve_point.point_index] = curve_point

    def remove_point(self, curve_point):
        self.points.remove(curve_point)
        if curve_point.curve_index not in self.point_indices:
            self.point_indices[curve_point.curve_index] = dict()
        if curve_point.point_index in self.point_indices[curve_point.curve_index]:
            del self.point_indices[curve_point.curve_index][curve_point.point_index]

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        if self.abs_anchor_at:
            elm.attrib["anchor_at"] = self.abs_anchor_at.to_text()
        for point in self.points:
            elm.append(point.get_xml_element())
        return elm

    def shift(self, curve_index, from_point_index=0,
             point_index_shift=0, curve_index_shift=0):
        for point in self.points:
            if point.curve_index != curve_index:
                continue
            if point.point_index<from_point_index:
                continue
            point.point_index += point_index_shift
            point.curve_index += curve_index_shift

    def reverse_shift(self, curve_index, point_index_max):
        for point in self.points:
            if point.curve_index != curve_index:
                continue
            point.point_index = point_index_max-point.point_index

    def delete_curve(self, curve_index):
        i = 0
        while i<len(self.points):
            point = self.points[i]
            if point.curve_index == curve_index:
                del self.points[i]
            else:
                i += 1

    def delete_point_index(self, curve_index, point_index):
        i = 0
        while i<len(self.points):
            point = self.points[i]
            if point.curve_index == curve_index and point.point_index == point_index:
                del self.points[i]
            else:
                i += 1

    def update_closed_curves(self, curves):
        for curve_index in self.point_indices:
            if curve_index>=len(curves):
                continue
            curve = curves[curve_index]
            if not curve.closed:
                continue
            last_index = len(curve.bezier_points)-1
            point_indices = self.point_indices[curve_index]
            if last_index in point_indices:
                last_bezier_point = curve.bezier_points[last_index]
                curve.origin.copy_from(last_bezier_point.dest)

    @classmethod
    def create_from_xml_element(cls, elm):
        point_group = cls()
        anchor_at_str = elm.attrib.get("anchor_at", None)
        if anchor_at_str:
            point_group.abs_anchor_at = Point.from_text(anchor_at_str)
        for point_elm in elm.findall(CurvePoint.TAG_NAME):
            point = CurvePoint.create_from_xml_element(point_elm)
            if point:
                point_group.add_point(point)
        if len(point_group.points) < 2:
            return None
        return point_group
