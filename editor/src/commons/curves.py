from bezier_point import BezierPoint
from point import Point, RAD_PER_DEG
from rect import Rect
from xml.etree.ElementTree import Element as XmlElement
import numpy, math
from scipy.spatial import distance, KDTree


class NaturalCurve(object):
    TAG_NAME = "curve"

    def __init__(self, origin, bezier_points=None, closed=False):
        self.origin = origin
        self.bezier_points = []
        #TODO
        # bare points are more easing the erasing of freely drawn curves.
        # for normal small curves, this element needs to be out of
        # operation. some checks necessary to implement it.
        self.bare_point_xys = numpy.array([(origin.x, origin.y)])
        self.all_points = numpy.array([(origin.x, origin.y)])
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
        newob.all_points = self.all_points.copy()
        return newob

    def copy_from(self, other_curve):
        self.origin.copy_from(other_curve.origin)
        for i in range(min(len(self.bezier_points), len(other_curve.bezier_points))):
            self_bzpoint = self.bezier_points[i]
            other_bzpoint = other_curve.bezier_points[i]
            self_bzpoint.control_1.copy_from(other_bzpoint.control_1)
            self_bzpoint.control_2.copy_from(other_bzpoint.control_2)
            self_bzpoint.dest.copy_from(other_bzpoint.dest)

    def set_inbetween(self, start_curve, start_wh, end_curve, end_wh, frac, this_wh):
        start_curve = start_curve.copy()
        start_curve.scale(start_wh[0], start_wh[1])

        end_curve = end_curve.copy()
        end_curve.scale(end_wh[0], end_wh[1])

        self.origin.set_inbetween(start_curve.origin, end_curve.origin, frac)
        minp = min(len(self.bezier_points), \
                        len(start_curve.bezier_points), \
                               len(end_curve.bezier_points))
        i = 0
        while i<minp:
            self_bzpoint = self.bezier_points[i]
            start_bzpoint = start_curve.bezier_points[i]
            end_bzpoint = end_curve.bezier_points[i]
            i +=1
            self_bzpoint.control_1.set_inbetween( start_bzpoint.control_1, end_bzpoint.control_1, frac)
            self_bzpoint.control_2.set_inbetween(start_bzpoint.control_2, end_bzpoint.control_2, frac)
            self_bzpoint.dest.set_inbetween(start_bzpoint.dest, end_bzpoint.dest, frac)

        self.scale(1./this_wh[0], 1./this_wh[1])

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

    def draw_path(self, ctx, new_path=True):
        if new_path:
            ctx.new_path()
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

    def get_baked_points(self, width, height, detailed=False):
        """
        This will generate the points along the path of curve.
        Curve has normalized points. So, width and height are provided.
        The baking or precalculation of pixels points in this way
        helps to implement path following feature.
        The distance between to points are kept one pixel along diagonal.
        """
        diagonal = math.sqrt(width*width+height*height)
        path_points = numpy.array([], dtype="f")

        prev_tp = self.origin.copy()
        elapsed_dist = 0
        for bezier_point_index in range(len(self.bezier_points)):
            bezier_point = self.bezier_points[bezier_point_index]
            if bezier_point_index == 0:
                p0 = self.origin
            else:
                p0 = self.bezier_points[bezier_point_index-1].dest
            p1 = bezier_point.control_1
            p2 = bezier_point.control_2
            p3 = bezier_point.dest

            dist = p0.distance(p1) + p1.distance(p2) + p2.distance(p3)
            dist = int(round(dist*diagonal))
            for i in range(dist):
                t = i*1.0/dist
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

                this_tp = Point(tx, ty)
                t_dist = int(round(prev_tp.distance(this_tp)*diagonal))
                if t_dist == 0:
                    continue
                prev_tp = this_tp
                ts_step = 1./t_dist
                for ts in range(1, t_dist+1):
                    ts *= ts_step
                    nx = prev_tp.x + ts*(tx-prev_tp.x)
                    ny = prev_tp.y + ts*(ty-prev_tp.y)
                    if detailed:
                        path_points = numpy.append(path_points, [nx, ny, bezier_point_index, t])
                    else:
                        path_points = numpy.append(path_points, [nx, ny])

        if detailed:
            path_points.shape =(-1, 4)
        else:
            path_points.shape =(-1, 2)
        return path_points

    def get_closest_control_point(self, point, width, height, tolerance):
        baked_points = self.get_baked_points(width, height, detailed=True)
        kd_tree = KDTree(baked_points[:, :2])
        distance, index = kd_tree.query([point.x, point.y])
        if distance<=tolerance:
            bkp = baked_points[index]
            beizer_point_index = int(bkp[2])
            t = bkp[3]
            return beizer_point_index, t
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
            if hasattr(self, "bare_point_xys"):
                self.bare_point_xys=numpy.insert(self.bare_point_xys, bezier_point_index+1,
                        [(post_bzp.dest.x, post_bzp.dest.y)], axis=0)
        return post_bzp

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

class PseudoPoint(Point):
    def __init__(self, curve, index):
        self.curve = curve
        self.index = index

    def __getattr__(self, name):
        if self.index>=self.curve.all_points.shape[0]:
            self.index = self.curve.all_points.shape[0]-1
        if name == "x":
            return self.curve.all_points[self.index][0]
        elif name == "y":
            return self.curve.all_points[self.index][1]
        else:
            raise AttributeError

    def __setattr__(self, name, value):
        if name == "x":
            self.curve.all_points[self.index][0] = value
        elif name == "y":
            self.curve.all_points[self.index][1] = value
        else:
            super(PseudoPoint, self).__setattr__(name, value)

    def copy(self):
        return Point(self.x, self.y)

class PseudoBezierPoint(BezierPoint):
    def __init__(self, curve, index):
        self.curve = curve
        self.index = index
        self.control_1  = PseudoPoint(self.curve, self.index*3+0+1)
        self.control_2  = PseudoPoint(self.curve, self.index*3+1+1)
        self.dest  = PseudoPoint(self.curve, self.index*3+2+1)

    def copy(self):
        return BezierPoint(self.control_1.copy(), self.control_2.copy(), self.dest.copy())

class PseudoBezierPoints(object):
    def __init__(self, curve):
        self.curve = curve
        self.pseudo_points = dict()

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index.start is None:
                start_i = 0
            else:
                start_i = index.start
            if index.stop is None:
                stop_i = len(self)
            else:
                stop_i = index.stop

            if index.step is None:
                if start_i<stop_i:
                    step_i = 1
                else:
                    step_i = -1
            else:
                step_i = inde.step
            return [self[i] for i in xrange(start_i, stop_i, step_i)]
        if index<0:
            index += len(self)
        if index>=len(self):
            return None
        if index not in self.pseudo_points:
            self.pseudo_points[index] = PseudoBezierPoint(self.curve, index)
        return self.pseudo_points[index]

    def __len__(self):
        return (len(self.curve.all_points)-1)/3

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __delitem__(self, index):
        indices = []
        if isinstance(index, slice):
            start = index.start
            step = 1 if index.step is None else index.step
            stop = len(self)+1 if index.stop is None else index.stop
            for i in range(start, stop, step):
                indices.extend([i*3+0+1, i*3+1+1, i*3+2+1])
        else:
            indices.extend([index*3+0+1, index*3+1+1, index*3+2+1])
        self.curve.all_points = numpy.delete(self.curve.all_points,indices, axis=0)

    def insert(self, index, bezier_point):
        self.curve.insert_bezier_point(index, bezier_point)

    def extend(self, bezier_points):
        for bezier_point in bezier_points:
            self.curve.add_bezier_point(bezier_point)

#to use normal pythonian curve
class Curve(NaturalCurve):
    pass

#this is numpy-ian curve
class Curve(NaturalCurve):
    def __init__(self, origin, bezier_points=None, closed=False):
        self.all_points = numpy.array([(origin.x, origin.y)])
        if bezier_points is not None:
            self.add_bezier_points(bezier_points)
        self.closed = closed
        self.origin = PseudoPoint(self, 0)
        self.bezier_points = PseudoBezierPoints(self)

    def adjust_origin(self):
        if not self.closed:
            return
        self.all_points[0][0] = self.all_points[-1][0]
        self.all_points[0][1] = self.all_points[-1][1]

    def copy(self):
        newob = Curve(self.origin.copy(), closed=self.closed)
        newob.all_points = self.all_points.copy()
        return newob

    def reverse_copy(self):
        newob = Curve(self.bezier_points[-1].dest.copy(), closed=self.closed)
        newob.all_points = self.all_points[::-1].copy()
        return newob

    def append_curve(self, other):
        if self.closed or other.closed:
            return
        self.all_points = self.all_points + other.all_points[1:]

    def copy_from(self, other_curve):
        ml = min(self.all_points.shape[0], other_curve.all_points.shape[0])
        self.all_points[:ml] = numpy.copy(other_curve.all_points[:ml])
        self.all_points[ml:] = numpy.copy(other_curve.all_points[-1])
        self.adjust_origin()

    def add_bezier_point(self, bezier_point):
        self.all_points=numpy.append(self.all_points,
            [(bezier_point.control_1.x, bezier_point.control_1.y),
             (bezier_point.control_2.x, bezier_point.control_2.y),
             (bezier_point.dest.x, bezier_point.dest.y)], axis=0)

    def insert_bezier_point(self, index, bezier_point):
        self.all_points=numpy.insert(self.all_points, index*3+1,
            [(bezier_point.control_1.x, bezier_point.control_1.y),
             (bezier_point.control_2.x, bezier_point.control_2.y),
             (bezier_point.dest.x, bezier_point.dest.y)], axis=0)

    def remove_bezier_point_index(self, index):
        if index<0:
            index += len(self.bezier_points)
        self.all_points=numpy.delete(self.all_points,
            [index*3+0+1, index*3+1+1, index*3+2+1], axis=0)

    def remove_bezier_point_indices(self, start_index, end_index):
        for i in range(end_index-1, start_index-1, -1):
            self.all_points=numpy.delete(self.all_points, [i*3+0+1, i*3+1+1, i*3+2+1], axis=0)

    def update_bezier_point_index(self, index):
        pass

    def update_origin(self):
        pass

    def get_outline(self):
        outline = None
        if len(self.all_points)==1:
            return outline
        left, top = numpy.min(self.all_points, axis=0)
        right, bottom = numpy.max(self.all_points, axis=0)
        return Rect(left, top, right-left, bottom-top)

    def translate(self, dx, dy):
        self.all_points = self.all_points + numpy.array([(dx, dy)])

    def scale(self, sx ,sy):
        self.all_points = numpy.multiply(self.all_points, [sx, sy])

    def set_inbetween(self, start_curve, start_wh, end_curve, end_wh, frac, this_wh):
        ml = min(start_curve.all_points.shape[0],
                 end_curve.all_points.shape[0],
                 self.all_points.shape[0])
        self.all_points[:ml] = (start_curve.all_points[:ml]*start_wh)*(1-frac) + \
                               (end_curve.all_points[:ml]*end_wh)*frac
        self.all_points[ml:] = numpy.copy(self.all_points[ml-1])
        self.all_points = numpy.multiply(self.all_points, (1./this_wh[0], 1./this_wh[1]))
        self.adjust_origin()

    def draw_path(self, ctx, new_path=True, line_to=False):
        if new_path:
            ctx.new_path()
        if line_to:
            ctx.line_to(self.all_points[0][0], self.all_points[0][1])
        else:
            ctx.move_to(self.all_points[0][0], self.all_points[0][1])
        for i in range(1, len(self.all_points), 3):
            ctx.curve_to(
                self.all_points[i][0], self.all_points[i][1],
                self.all_points[i+1][0], self.all_points[i+1][1],
                self.all_points[i+2][0], self.all_points[i+2][1])
        if len(self.all_points) > 2 and self.closed:
            ctx.close_path()

    def reverse_draw_path(self, ctx, new_path=True, line_to=False):
        if new_path:
            ctx.new_path()
        if line_to:
            ctx.line_to(self.all_points[-1][0], self.all_points[-1][1])
        else:
            ctx.move_to(self.all_points[-1][0], self.all_points[-1][1])
        for i in xrange(len(self.all_points)-2, 1,-3):
            c1 = self.all_points[i]
            c2 = self.all_points[i-1]
            ds = self.all_points[i-2]
            ctx.curve_to(
                c1[0], c1[1],
                c2[0], c2[1],
                ds[0], ds[1])
        if len(self.all_points) > 2 and self.closed:
            ctx.close_path()

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
        self.position = Point(0, 0)

    def __repr__(self):
        return "CurvePoint(curve_index={0}, point_index={1}, point_type={2}".format(
            self.curve_index, self.point_index, self.point_type)

    def copy(self):
        newob = CurvePoint(self.curve_index, self.point_index, self.point_type)
        newob.position.copy_from(self.position)
        return newob

    def get_point(self, curves):
        if self.curve_index>=len(curves):
            return None
        curve = curves[self.curve_index]
        if self.point_index>= len(curve.bezier_points):
            return None
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

    def update_original(self, point, curves):
        original_point = self.get_point(curves)
        if original_point:
            original_point.copy_from(point)
        if self.point_type == CurvePoint.POINT_TYPE_DEST:
            if self.curve_index>=len(curves):
                return
            curve = curves[self.curve_index]
            if curve.closed and self.point_index == len(curve.bezier_points)-1:
                curve.origin.copy_from(point)

    def __eq__(self, other):
        return (self.curve_index == other.curve_index and \
                self.point_index == other.point_index and \
                self.point_type == other.point_type)

    def get_key(self):
        return hash("{0}{1}{2}".format(self.curve_index, self.point_index, self.point_type))

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["ci"] = "{0}".format(self.curve_index)
        elm.attrib["pi"] = "{0}".format(self.point_index)
        elm.attrib["pt"] = "{0}".format(self.point_type)
        elm.attrib["ps"] = self.position.to_text()
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        curve_index = int(elm.attrib.get("ci", -1))
        point_index = int(elm.attrib.get("pi", -1))
        point_type = int(elm.attrib.get("pt", -1))
        if curve_index<0:
            return None
        curve_point = cls(curve_index, point_index, point_type)
        curve_point.position.copy_from(Point.from_text(elm.attrib.get("ps", Point(0,0).to_text())))
        return curve_point

class CurvePointGroup(object):
    TAG_NAME = "curve_point_group"

    def __init__(self):
        self.points = dict()
        self.point_indices = dict()

    def __repr__(self):
        return "CurvePointGroup([{0}])".format(",\n".join(str(p) for p in self.points))

    def copy(self):
        newob = CurvePointGroup()
        for curve_point in self.points.values():
            newob.add_point(curve_point.copy())
        return newob

    def contain(self, curve_point):
        return curve_point in self.points

    def add_point(self, curve_point):
        if curve_point.get_key() in self.points:
            return False
        self.points[curve_point.get_key()] = curve_point
        if curve_point.curve_index not in self.point_indices:
            self.point_indices[curve_point.curve_index] = dict()
        self.point_indices[curve_point.curve_index][curve_point.point_index] = curve_point
        return True

    def remove_point(self, curve_point):
        if curve_point.get_key() not in self.points:
            return False
        del self.points[curve_point.get_key()]
        if curve_point.curve_index not in self.point_indices:
            self.point_indices[curve_point.curve_index] = dict()
        if curve_point.point_index in self.point_indices[curve_point.curve_index]:
            del self.point_indices[curve_point.curve_index][curve_point.point_index]
        return True

    def get_point(self, curve_point):
        return self.points.get(curve_point.get_key())

    def remove_bezier_point_index(self, curve_index, point_index):
        delete_points = []
        for point in self.points.values():
            if point.point_type == CurvePoint.POINT_TYPE_ORIGIN:
                continue
            if point.curve_index == curve_index and point_index == index:
                delete_points.append(point)
        for point in delete_points:
            del self.points[point.get_key()]

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        for point in self.points.values():
            elm.append(point.get_xml_element())
        return elm

    def shift(self, curve_index, from_point_index=0,
             point_index_shift=0, curve_index_shift=0, to_point_index=-1):
        for point in self.points.values():
            if point.curve_index != curve_index:
                continue
            if point.point_index<from_point_index:
                continue
            if to_point_index>=0 and point.point_index>=to_point_index:
                continue
            point.point_index += point_index_shift
            point.curve_index += curve_index_shift

    def reverse_shift(self, curve_index, point_index_max):
        for point in self.points.values():
            if point.curve_index != curve_index:
                continue
            point.point_index = point_index_max-point.point_index

    def delete_curve(self, curve_index):
        i = 0
        while key in self.points.keys():
            point = self.points[key]
            if point.curve_index == curve_index:
                del self.points[key]
            else:
                i += 1

    def delete_point_index(self, curve_index, point_index):
        i = 0
        while key in self.points.keys():
            point = self.points[key]
            if point.curve_index == curve_index:
                if point.point_index == point_index:
                    del self.points[key]
                    continue
                elif point.point_index > point_index:
                    point.point_index -= 1

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
    def create_from_xml_element(cls, elm, curves):
        point_group = cls()
        for point_elm in elm.findall(CurvePoint.TAG_NAME):
            point = CurvePoint.create_from_xml_element(point_elm)
            if point.curve_index>=len(curves):
                continue
            curve = curves[point.curve_index]
            if point.point_index>=len(curve.bezier_points):
                continue
            if point:
                point_group.add_point(point)
        return point_group

