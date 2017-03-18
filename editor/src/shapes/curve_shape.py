from ..commons import *
from shape import Shape
from xml.etree.ElementTree import Element as XmlElement
from mirror import *

class CurveShape(Shape, Mirror):
    TYPE_NAME = "curve_shape"
    FORM_TAG_NAME = "form"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height):
        Shape.__init__(self, anchor_at, border_color, border_width, fill_color, width, height)
        Mirror.__init__(self)
        self.curves = []
        self.forms = dict()
        self.show_points = True
        self.point_groups = []

    def add_point_group(self, point_group):
        self.point_groups.append(point_group)
        return point_group

    def delete_point_group(self, point_group):
        self.point_groups.remove(point_group)
        return point_group

    def copy_data_from_linked(self):
        if not self.linked_to: return
        del self.curves[:]

        linked_to_anchor_at = self.linked_to.anchor_at.copy()
        linked_to_anchor_at.scale(1./self.linked_to.width, 1./self.linked_to.height)

        self_anchor_at = self.anchor_at.copy()
        self_anchor_at.scale(1./self.width, 1./self.height)

        diff_x = self_anchor_at.x-linked_to_anchor_at.x
        diff_y = self_anchor_at.y-linked_to_anchor_at.y

        for curve in  self.linked_to.curves:
            curve = curve.copy()
            curve.translate(diff_x, diff_y)
            self.curves.append(curve)
        self.fit_size_to_include_all()
        self.forms = copy_dict(self.linked_to.forms)

    def save_form(self, form_name):
        if form_name is None:
            i = len(self.forms)
            while True:
                i += 1
                form_name = "Form_{0}".format(i)
                if form_name not in self.forms:
                    break
        curves = []
        anchor_at = self.anchor_at.copy()
        anchor_at.scale(1./self.width, 1./self.height)
        for curve in self.curves:
            curve = curve.copy()
            curve.origin.translate(-anchor_at.x, -anchor_at.y)
            for bzpoint in curve.bezier_points:
                bzpoint.control_1.translate(-anchor_at.x, -anchor_at.y)
                bzpoint.control_2.translate(-anchor_at.x, -anchor_at.y)
                bzpoint.dest.translate(-anchor_at.x, -anchor_at.y)
            curves.append(curve)
        form_dict = dict()
        form_dict["curves"] = curves
        form_dict["width"] = self.width
        form_dict["height"] = self.height
        self.forms[form_name] = dict(form_dict)
        return form_name

    def set_form(self, form_name):
        form_dict = self.forms[form_name]

        diff_width = form_dict["width"] - self.width
        diff_height = form_dict["height"] - self.height
        abs_anchor_at = self.get_abs_anchor_at()

        self.width = form_dict["width"]
        self.height = form_dict["height"]
        form_curves = form_dict["curves"]

        anchor_at = self.anchor_at.copy()
        anchor_at.scale(1./self.width, 1./self.height)

        for i in range(min(len(form_curves), len(self.curves))):
            self_curve = self.curves[i]
            form_curve = form_curves[i]
            self_curve.origin.copy_from(form_curve.origin)
            self_curve.origin.translate(anchor_at.x, anchor_at.y)
            for j in range(min(len(self_curve.bezier_points), len(form_curve.bezier_points))):
                self_bzpoint = self_curve.bezier_points[j]
                form_bzpoint = form_curve.bezier_points[j]
                self_bzpoint.control_1.copy_from(form_bzpoint.control_1)
                self_bzpoint.control_2.copy_from(form_bzpoint.control_2)
                self_bzpoint.dest.copy_from(form_bzpoint.dest)

                self_bzpoint.control_1.translate(anchor_at.x, anchor_at.y)
                self_bzpoint.control_2.translate(anchor_at.x, anchor_at.y)
                self_bzpoint.dest.translate(anchor_at.x, anchor_at.y)

        #self.anchor_at.translate(diff_width, diff_height)
        self.fit_size_to_include_all()
        self.move_to(abs_anchor_at.x, abs_anchor_at.y)


    def set_prop_value(self, prop_name, value, prop_data=None):
        if prop_name == "internal":
            start_form = prop_data["start_form"]
            end_form = prop_data["end_form"]

            if end_form is None or end_form not in self.forms:
                self.set_form(start_form)
                return

            start_form_dict = self.forms[start_form]
            end_form_dict = self.forms[end_form]

            new_width = start_form_dict["width"] + (end_form_dict["width"]-start_form_dict["width"])*value
            new_height = start_form_dict["height"] + (end_form_dict["height"]-start_form_dict["height"])*value

            diff_width = new_width - self.width
            diff_height = new_height - self.height

            abs_anchor_at = self.get_abs_anchor_at()

            self.width = new_width
            self.height = new_height
            start_form_curves = start_form_dict["curves"]
            end_form_curves = end_form_dict["curves"]

            anchor_at = self.anchor_at.copy()
            anchor_at.scale(1./self.width, 1./self.height)

            for i in range(min(len(start_form_curves), len(end_form_curves), len(self.curves))):
                self_curve = self.curves[i]
                start_form_curve = start_form_curves[i]
                end_form_curve = end_form_curves[i]

                self_curve.origin.set_inbetween(start_form_curve.origin, end_form_curve.origin, value)
                self_curve.origin.translate(anchor_at.x, anchor_at.y)
                for j in range(min(len(self_curve.bezier_points), len(start_form_curve.bezier_points), \
                                   len(end_form_curve.bezier_points) )):
                    self_bzpoint = self_curve.bezier_points[j]
                    start_form_bzpoint = start_form_curve.bezier_points[j]
                    end_form_bzpoint = end_form_curve.bezier_points[j]

                    self_bzpoint.control_1.set_inbetween(
                        start_form_bzpoint.control_1, end_form_bzpoint.control_1, value)
                    self_bzpoint.control_2.set_inbetween(
                        start_form_bzpoint.control_2, end_form_bzpoint.control_2, value)
                    self_bzpoint.dest.set_inbetween(
                        start_form_bzpoint.dest, end_form_bzpoint.dest, value)

                    self_bzpoint.control_1.translate(anchor_at.x, anchor_at.y)
                    self_bzpoint.control_2.translate(anchor_at.x, anchor_at.y)
                    self_bzpoint.dest.translate(anchor_at.x, anchor_at.y)

            #self.anchor_at.translate(diff_width, diff_height)
            self.fit_size_to_include_all()
            self.move_to(abs_anchor_at.x, abs_anchor_at.y)
        else:
            Shape.set_prop_value(self, prop_name, value, prop_data)

    def rename_form(self, old_form, new_form):
        if new_form in self.forms: return
        self.forms[new_form] = self.forms[old_form]
        del self.forms[old_form]

    def get_xml_element(self):
        elm = Shape.get_xml_element(self)
        for curve in self.curves:
            elm.append(curve.get_xml_element())
        if not self.show_points:
            elm.attrib["show_points"] = "False"

        for form_name, form in self.forms.items():
            form_elm = XmlElement(self.FORM_TAG_NAME)
            form_elm.attrib["name"] = form_name
            form_elm.attrib["width"] = "{0}".format(form["width"])
            form_elm.attrib["height"] = "{0}".format(form["height"])
            for curve in form["curves"]:
                form_elm.append(curve.get_xml_element())
            elm.append(form_elm)

        for point_group in self.point_groups:
            elm.append(point_group.get_xml_element())

        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        arr = Shape.get_params_array_from_xml_element(elm)
        shape = cls(*arr)
        shape.show_points = (elm.attrib.get("show_points", "True") != "False")
        default_point = Point(0,0)

        for curve_elm in elm.findall(Curve.TAG_NAME):
            curve = Curve.create_from_xml_element(curve_elm)
            shape.curves.append(curve)

        for form_elm in elm.findall(cls.FORM_TAG_NAME):
            form_name = form_elm.attrib["name"]
            form_dict = dict()
            form_dict["width"] = float(form_elm.attrib["width"])
            form_dict["height"] = float(form_elm.attrib["height"])
            form_dict["curves"] = curves = []
            for curve_elm in form_elm.findall(Curve.TAG_NAME):
                curves.append(Curve.create_from_xml_element(curve_elm))
            shape.forms[form_name] = form_dict

        for point_group_elm in elm.findall(CurvePointGroup.TAG_NAME):
            point_group = CurvePointGroup.create_from_xml_element(point_group_elm)
            if point_group:
                shape.point_groups.append(point_group)

        shape.assign_params_from_xml_element(elm)
        return shape

    def copy(self, copy_name=False, deep_copy=False):
        newob = CurveShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                            color_copy(self.fill_color), self.width, self.height)
        self.copy_into(newob, copy_name)
        for curve in self.curves:
            newob.curves.append(curve.copy())
        if deep_copy:
            newob.forms = copy_dict(self.forms)
        newob.show_points = self.show_points
        return newob

    def is_empty(self):
        return len(self.curves) == 0

    def add_curve(self, curve):
        self.curves.append(curve)
        self.fit_size_to_include_all()

    def _draw_curve(self, ctx, curve, scale=None, angle=None):
        ctx.save()
        if angle is not None:
            ctx.translate(self.anchor_at.x, self.anchor_at.y)
            ctx.rotate(angle*RAD_PER_DEG)
            ctx.translate(-self.anchor_at.x, -self.anchor_at.y)
        ctx.scale(self.width, self.height)
        if scale:
            if scale[0] == -1 and scale[1] == 1:
                ctx.translate(2*self.anchor_at.x/self.width, 0)
            elif scale[0] == 1 and scale[1] == -1:
                ctx.translate(0, 2*self.anchor_at.y/self.height)
            elif scale[0] == -1 and scale[1] == -1:
                ctx.translate(2*self.anchor_at.x/self.width, 2*self.anchor_at.y/self.height)
            ctx.scale(*scale)
        ctx.new_path()
        ctx.move_to(curve.origin.x, curve.origin.y)
        for bezier_point in curve.bezier_points:
            ctx.curve_to(
                bezier_point.control_1.x, bezier_point.control_1.y,
                bezier_point.control_2.x, bezier_point.control_2.y,
                bezier_point.dest.x, bezier_point.dest.y)
        if len(curve.bezier_points) > 1 and curve.closed:
            ctx.close_path()
        ctx.restore()

    def draw_path(self, ctx, for_fill=False):
        paths = []
        for curve in self.curves:
            if not for_fill or (for_fill and curve.closed):
                self._draw_curve(ctx, curve)
                paths.append(ctx.copy_path())
        if self.mirror != 0:
            scales, rotations = self.get_scales_n_rotations()

            for scale in scales:
                for curve in self.curves:
                    if not for_fill or (for_fill and curve.closed):
                        self._draw_curve(ctx, curve, scale=scale)
                        paths.append(ctx.copy_path())

            for angle in rotations:
                for curve in self.curves:
                    if not for_fill or (for_fill and curve.closed):
                        self._draw_curve(ctx, curve, angle=angle)
                        paths.append(ctx.copy_path())
        ctx.new_path()
        for path in paths:
            ctx.append_path(path)

    def fit_size_to_include_all(self):
        outline = None
        for curve in self.curves:
            if outline is None:
                outline = curve.get_outline()
            else:
                outline.expand_include(curve.get_outline())
        if not outline: return
        abs_anchor_at = self.get_abs_anchor_at()
        self.anchor_at.translate(-self.width*outline.left, -self.height*outline.top)
        self.move_to(abs_anchor_at.x, abs_anchor_at.y)
        self.set_width(outline.width*self.width)
        self.set_height(outline.height*self.height)

        if outline.height==0:
            sy = None
        else:
            sy = 1/outline.height
        if outline.width==0:
            sx = None
        else:
            sx = 1/outline.width

        for curve in self.curves:
            curve.translate(-outline.left, -outline.top)
            if sx is not None and sy is not None:
                curve.scale(sx, sy)

    def find_point_location(self, point):
        point = point.copy()
        point.scale(1./self.width, 1./self.height)
        for curve_index in range(len(self.curves)):
            curve = self.curves[curve_index]
            found = curve.get_closest_control_point(point, self.width, self.height)
            if found:
                bezier_point_index, t = found
                return (curve_index, bezier_point_index, t)
        return None

    def insert_point_at(self, point):
        found = self.find_point_location(point)
        if not found: return False
        curve_index, bezier_point_index, t = found
        curve = self.curves[curve_index]
        curve.insert_point_at(bezier_point_index, t)
        return True

    def insert_break_at(self, curve_index, bezier_point_index):
        if curve_index>=len(self.curves): return False
        prev_curve = self.curves[curve_index]
        if bezier_point_index>= len(prev_curve.bezier_points): return False
        if bezier_point_index == len(prev_curve.bezier_points)-1:
            if prev_curve.closed:
                #Just open up the closed curve
                prev_curve.closed = False
                return True
            else:
                return False
        bezier_point = prev_curve.bezier_points[bezier_point_index]
        new_curve = Curve(origin=bezier_point.dest.copy(),
                          bezier_points=prev_curve.bezier_points[bezier_point_index+1:])
        prev_curve.remove_bezier_point_indices(bezier_point_index+1, len(prev_curve.bezier_points))
        prev_curve.closed = False

        self.curves.insert(curve_index+1, new_curve)
        return True

    def join_points(self, curve_index_1, is_start_1, curve_index_2, is_start_2):
        if curve_index_1>=len(self.curves): return False
        if curve_index_1>=len(self.curves): return False

        curve_1 = self.curves[curve_index_1]
        curve_2 = self.curves[curve_index_2]

        if curve_index_1 == curve_index_2:
            if is_start_1 != is_start_2:
                curve_1.closed = True
                curve_1.origin.x =  (curve_1.origin.x+curve_1.bezier_points[-1].dest.x)*.5
                curve_1.origin.y =  (curve_1.origin.y+curve_1.bezier_points[-1].dest.y)*.5
                curve_1.bezier_points[-1].dest.copy_from(curve_1.origin)
                return True
            return False
        if curve_1.closed: return False
        if curve_2.closed: return False

        dist_lapse = .01
        if is_start_1 == is_start_2:#reverse curve_2
            rev_curve = curve_2.reverse_copy()
            curve_2.origin.copy_from(rev_curve.origin)
            for bpi in range(len(rev_curve.bezier_points)):
                curve_2.bezier_points[bpi].control_1.copy_from(rev_curve.bezier_points[bpi].control_1)
                curve_2.bezier_points[bpi].control_2.copy_from(rev_curve.bezier_points[bpi].control_2)
                curve_2.bezier_points[bpi].dest.copy_from(rev_curve.bezier_points[bpi].dest)

        if is_start_1:#swap curves
            curve_1, curve_2 = curve_2, curve_1
            curve_index_1, curve_index_2 = curve_index_2, curve_index_1

        #curve_2 get attached at the end of curve_1
        curve_1.bezier_points[-1].dest.x = (curve_1.bezier_points[-1].dest.x +  curve_2.origin.x)*.5
        curve_1.bezier_points[-1].dest.y = (curve_1.bezier_points[-1].dest.y +  curve_2.origin.y)*.5

        curve_1.add_bezier_points(curve_2.bezier_points)
        del self.curves[curve_index_2]
        return True

    def delete_point_at(self, curve_index, bezier_point_index, break_allowed=False):
        if curve_index>=len(self.curves): return False
        curve = self.curves[curve_index]
        if bezier_point_index>=len(curve.bezier_points): return False
        if bezier_point_index<-1: return False

        if len(curve.bezier_points)>1:
            if bezier_point_index == -1:
                curve.origin.copy_from(curve.bezier_points[0].dest)
                curve.update_origin()
                curve.remove_bezier_point_index(0)
                if curve.closed:
                    curve.bezier_points[-1].dest.copy_from(curve.origin)
                    curve.update_bezier_point_index(-1)#
            elif bezier_point_index == len(curve.bezier_points)-1:
                if curve.closed and curve.bezier_points:
                    curve.origin.copy_from(curve.bezier_points[0].dest)
                    curve.bezier_points[-1].dest.copy_from(curve.origin)
                    curve.update_bezier_point_index(-1)#
                    curve.remove_bezier_point_index(0)
                else:
                    curve.remove_bezier_point_index(-1)
            else:
                if break_allowed:
                    new_curve = Curve(origin=curve.bezier_points[bezier_point_index].dest.copy())
                    new_curve.add_bezier_points(curve.bezier_points[bezier_point_index+1:])
                    curve.remove_bezier_point_indices(
                        bezier_point_index+1, len(curve.bezier_points))
                    self.curves.insert(curve_index+1, new_curve)
                curve.remove_bezier_point_index(bezier_point_index)

            if len(curve.bezier_points)<3:
                curve.closed = False
            if len(self.curves)>1:
                if (len(curve.bezier_points)<=1 and curve.closed) or len(curve.bezier_points)==0:
                    del self.curves[curve_index]
        elif len(self.curves)>1:
            del self.curves[curve_index]

        return True

    def delete_dest_points_inside_rect(self, center, radius):
        center = self.transform_point(center)
        radius /= (self.width+self.height)*.5
        center.scale(1./self.width, 1./self.height)
        curve_point_indices = dict()

        for curve_index in range(len(self.curves)):
            curve = self.curves[curve_index]
            curve_point_indices[curve_index] = curve.get_indices_within(center, radius)
            #for bezier_point_index in range(-1, len(curve.bezier_points)):
            #    if bezier_point_index == -1:
            #        point = curve.origin.copy()
            #    else:
            #        point = curve.bezier_points[bezier_point_index].dest.copy()
            #    if point.distance(center)<radius:
            #        if curve_index not in curve_point_indices:
            #            curve_point_indices[curve_index] = []
            #        curve_point_indices[curve_index].append(bezier_point_index)
        delete_count = 0
        for curve_index in reversed(sorted(curve_point_indices.keys())):
            for bezier_point_index in reversed(sorted(curve_point_indices[curve_index])):
                if self.delete_point_at(curve_index, bezier_point_index, break_allowed=True):
                    delete_count += 1
        return delete_count>0

    @staticmethod
    def create_from_rectangle_shape(rectangle_shape):
        if rectangle_shape.corner_radius==0: return None
        curve_shape = CurveShape(Point(0,0), None, None, None, None, None)
        crsx = rectangle_shape.corner_radius/rectangle_shape.width
        crsy = rectangle_shape.corner_radius/rectangle_shape.height
        k = .5522847498*.5#magic number
        #crsx = crsy = .5
        curved_points = [
            BezierPoint(control_1=Point(.5+k, 0), control_2=Point(1., .5-k), dest=Point(1., .5)),
            BezierPoint(control_1=Point(1., .5+k), control_2=Point(.5+k, 1.), dest=Point(.5, 1.)),
            BezierPoint(control_1=Point(.5-k, 1.), control_2=Point(0, .5+k), dest=Point(0., .5)),
            BezierPoint(control_1=Point(0., .5-k), control_2=Point(0.5-k, 0.), dest=Point(.5, 0.))
        ]
        curved_points[0].scale(2*crsx, 2*crsy).translate(1.-2*crsx, 0)
        curved_points[1].scale(2*crsx, 2*crsy).translate(1.-2*crsx, 1-2*crsy)
        curved_points[2].scale(2*crsx, 2*crsy).translate(0, 1-2*crsy)
        curved_points[3].scale(2*crsx, 2*crsy).translate(0, 0)

        p1 = Point(1., 1-crsy)
        p2 = Point(crsx, 1.)
        p3 = Point(0., crsy)
        p4 = Point(1.-crsx, 0)

        final_points= [
            curved_points[0],
            BezierPoint(control_1=p1.copy(), control_2=p1.copy(), dest=p1.copy()),
            curved_points[1],
            BezierPoint(control_1=p2.copy(), control_2=p2.copy(), dest=p2.copy()),
            curved_points[2],
            BezierPoint(control_1=p3.copy(), control_2=p3.copy(), dest=p3.copy()),
            curved_points[3],
            BezierPoint(control_1=p4.copy(), control_2=p4.copy(), dest=p4.copy()),
        ]
        final_points[1].align_straight_with(final_points[0].dest)
        final_points[3].align_straight_with(final_points[2].dest)
        final_points[5].align_straight_with(final_points[4].dest)
        final_points[7].align_straight_with(final_points[6].dest)
        curve_shape.curves.append(Curve(
                origin=Point(1.-crsx, 0),
                bezier_points=final_points, closed=True))
        rectangle_shape.copy_into(curve_shape, all_fields=True, copy_name=False)
        curve_shape.fit_size_to_include_all()
        return curve_shape

    @staticmethod
    def create_from_oval_shape(oval_shape):
        curve_shape = CurveShape(Point(0,0), None, None, None, None, None)
        k = .5522847498*.5#magic number
        bezier_points = [
            BezierPoint(control_1=Point(.5+k, 0), control_2=Point(1., .5-k), dest=Point(1., .5)),
            BezierPoint(control_1=Point(1., .5+k), control_2=Point(.5+k, 1.), dest=Point(.5, 1.)),
            BezierPoint(control_1=Point(.5-k, 1.), control_2=Point(0, .5+k), dest=Point(0., .5)),
            BezierPoint(control_1=Point(0., .5-k), control_2=Point(0.5-k, 0.), dest=Point(.5, 0.))
        ]
        #curve_shape.curves.append(Curve(origin=Point(.5, 0.), bezier_points=bezier_points, closed=True))
        curve_shape.curves.append(Curve.create_circle(sweep_angle=oval_shape.sweep_angle))
        oval_shape.copy_into(curve_shape, all_fields=True, copy_name=False)
        curve_shape.fit_size_to_include_all()
        return curve_shape

    @staticmethod
    def create_from_polygon_shape(polygon_shape):
        curve_shape = CurveShape(Point(0,0), None, None, None, None, None)
        for polygon in polygon_shape.polygons:
            curve = None
            for i in range(len(polygon.points)):
                point = polygon.points[i]
                if i == 0:
                    curve = Curve(origin=point.copy())
                else:
                    bzp = BezierPoint(
                        control_1 = point.copy(), control_2 = point.copy(), dest = point.copy())
                    curve.add_bezier_point(bzp)
                    bzp.align_straight_with(polygon.points[i-1])
            curve.closed = polygon.closed
            if polygon.closed:
                point = polygon.points[0]
                bzp = BezierPoint(
                        control_1 = point.copy(), control_2 = point.copy(), dest = point.copy())
                curve.add_bezier_point(bzp)
                bzp.align_straight_with(polygon.points[-1])
            curve_shape.curves.append(curve)
        polygon_shape.copy_into(curve_shape, all_fields=True, copy_name=False)
        curve_shape.fit_size_to_include_all()
        return curve_shape

    def flip(self, direction):
        percent_anchor_at = self.anchor_at.copy()
        percent_anchor_at.scale(1./self.width, 1./self.height)
        for curve in self.curves:
            if direction == "x":
                curve.origin.x = 2*percent_anchor_at.x-curve.origin.x
            elif direction == "y":
                curve.origin.y = 2*percent_anchor_at.y-curve.origin.y
            for bezier_point in curve.bezier_points:
                if direction == "x":
                    bezier_point.control_1.x = 2*percent_anchor_at.x-bezier_point.control_1.x
                    bezier_point.control_2.x = 2*percent_anchor_at.x-bezier_point.control_2.x
                    bezier_point.dest.x = 2*percent_anchor_at.x-bezier_point.dest.x
                elif direction == "y":
                    bezier_point.control_1.y = 2*percent_anchor_at.y-bezier_point.control_1.y
                    bezier_point.control_2.y = 2*percent_anchor_at.y-bezier_point.control_2.y
                    bezier_point.dest.y = 2*percent_anchor_at.y-bezier_point.dest.y
        self.fit_size_to_include_all()

    def _transform_point_from_shape(self, shape, point):
        point.scale(shape.width, shape.height)
        point = shape.reverse_transform_point(point)
        point = self.transform_point(point)
        point.scale(1./self.width, 1./self.height)
        return point

    def include_inside(self, shape):
        if not isinstance(shape, CurveShape): return False
        for curve in shape.curves:
            curve = curve.copy()
            curve.origin = self._transform_point_from_shape(shape, curve.origin)
            for i in range(len(curve.bezier_points)):
                bp = curve.bezier_points[i]
                bp.control_1 = self._transform_point_from_shape(shape, bp.control_1)
                bp.control_2 = self._transform_point_from_shape(shape, bp.control_2)
                bp.dest = self._transform_point_from_shape(shape, bp.dest)
            self.curves.append(curve)
        return True
