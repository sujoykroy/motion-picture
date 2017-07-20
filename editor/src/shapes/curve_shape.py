from ..commons import *
from shape import Shape
from shape_list import ShapeList
from curves_form import CurvesForm
from curve_point_group_shape import CurvePointGroupShape
from xml.etree.ElementTree import Element as XmlElement
from mirror import *

REL_ABS_ANCHOR_AT = "rel_abs_anchor_at"

class CurveFormRenderer(object):
    def __init__(self, curve_shape, form_name):
        self.curve_shape = curve_shape
        self.form_name = form_name

    def get_name(self):
        return self.form_name

    def get_id(self):
        return self.form_name

    def get_pixbuf(self):
        curve_shape = self.curve_shape.copy()
        curve_shape.set_form_raw(self.curve_shape.get_form_by_name(self.form_name))
        curve_shape.reset_transformations()
        curve_shape.parent_shape = None
        pixbuf = curve_shape.get_pixbuf(64, 64)
        return pixbuf

class CurveShape(Shape, Mirror):
    TYPE_NAME = "curve_shape"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height):
        Shape.__init__(self, anchor_at, border_color, border_width, fill_color, width, height)
        Mirror.__init__(self)
        self.curves = []
        self.forms = dict()
        self.show_points = True
        self.point_group_shapes = ShapeList()
        self.baked_points = None
        self.form_pixbufs = dict()

    def get_form_pixbuf(self, form_name):
        if form_name not in self.form_pixbufs:
            curve_shape = self.copy()
            curve_shape.set_form_raw(self.get_form_by_name(form_name))
            curve_shape.reset_transformations()
            curve_shape.parent_shape = None
            pixbuf = curve_shape.get_pixbuf(64, 64)
            self.form_pixbufs[form_name] = pixbuf
        return self.form_pixbufs[form_name]

    def delete_form_pixbuf(self, form_name):
        if form_name in self.form_pixbufs:
            del self.form_pixbufs[form_name]

    def get_interior_shapes(self):
        return self.point_group_shapes

    def has_poses(self):
        return True

    @classmethod
    def get_pose_prop_names(cls):
        prop_names = super(CurveShape, cls).get_pose_prop_names()
        prop_names.extend(["form_raw"])
        return prop_names

    def replace_curves(self, curves):
        del self.curves[:]
        self.forms.clear()
        self.show_points = True
        self.point_group_shapes.clear()
        self.curves.extend(curves)

    def add_new_point_group_shape(self, point_group):
        point_group_shape = CurvePointGroupShape(curve_shape=self, curve_point_group=point_group)
        point_group_shape.build()
        self.point_group_shapes.add(point_group_shape)
        return point_group_shape

    def delete_point_group_shape(self, point_group_shape):
        self.point_group_shapes.remove(point_group_shape)
        return True

    def update_locked_curve_points(self):
        for point_group_shape in self.point_group_shapes:
            if not point_group_shape.locked_to_shape:
                point_group_shape.update_curve_points()

    def rename_shape(self, shape, name):
        old_name = shape.get_name()
        if self.point_group_shapes.rename(old_name, name):
            for form in self.forms.values():
                if not form.shapes_props:
                    continue
                if old_name in form.shapes_props:
                    form.shapes_props[name] = form.shapes_props[old_name]
                    del form.shapes_props[old_name]
        return True

    def get_point_group_shapes_model(self):
        model = [["", None]]
        for shape in self.point_group_shapes:
            model.append([shape.get_name(), shape])
        return model

    def copy_data_from_linked(self):
        super(CurveShape, self).copy_data_from_linked()

        if not self.linked_to: return

        self.forms = copy_value(self.linked_to.forms)
        self.form_pixbufs.clear()
        del self.curves[:]
        self.point_group_shapes.clear()

        if self.linked_to.point_group_shapes:
            abs_anchor_at = self.get_abs_anchor_at()
            self.anchor_at.copy_from(self.linked_to.anchor_at)
            for curve in self.linked_to.curves:
                self.curves.append(curve.copy())
            for point_group_shape in self.linked_to.point_group_shapes:
                point_group_shape = point_group_shape.copy(copy_name=True, deep_copy=True)
                point_group_shape.set_curve_shape(self)
                self.point_group_shapes.add(point_group_shape)
            self.build_interior_locked_to()
            self.move_to(abs_anchor_at.x, abs_anchor_at.y)
        else:
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

    def get_form_by_name(self, form):
        if form in self.forms:
            return self.forms[form]
        return None

    def get_form_raw(self):
        curves = []
        anchor_at = self.anchor_at.copy()
        anchor_at.scale(1./self.width, 1./self.height)
        for curve in self.curves:
            curve = curve.copy()
            curve.translate(-anchor_at.x, -anchor_at.y)
            curves.append(curve)

        if self.point_group_shapes:
            shapes_props = dict()
            for point_group_shape in self.point_group_shapes:
                prop_dict = point_group_shape.get_pose_prop_dict()
                shapes_props[point_group_shape.get_name()] = prop_dict
                if not point_group_shape.locked_to_shape:
                    rel_abs_anchor_at = point_group_shape.get_abs_anchor_at()
                    rel_abs_anchor_at.translate(-self.anchor_at.x, -self.anchor_at.y)
                    prop_dict[REL_ABS_ANCHOR_AT] = rel_abs_anchor_at
        else:
            shapes_props = None
        form = CurvesForm(width=self.width, height=self.height, curves=curves, shapes_props=shapes_props)
        return form

    def save_form(self, form_name):
        if form_name is None:
            i = len(self.forms)
            while True:
                i += 1
                form_name = "Form_{0}".format(i)
                if form_name not in self.forms:
                    break
        form = self.get_form_raw()
        form.set_name(form_name)
        self.forms[form_name] = form
        self.delete_form_pixbuf(form_name)
        return form_name

    def delete_form(self, form_name):
        if form_name in self.forms:
            del self.forms[form_name]
        self.delete_form_pixbuf(form_name)

    def set_form_raw(self, form):
        diff_width = form.width - self.width
        diff_height = form.height - self.height
        abs_anchor_at = self.get_abs_anchor_at()

        self.width = form.width
        self.height = form.height
        form_curves = form.curves

        anchor_at = self.anchor_at.copy()
        anchor_at.scale(1./self.width, 1./self.height)

        for i in range(min(len(form_curves), len(self.curves))):
            self_curve = self.curves[i]
            form_curve = form_curves[i]

            self_curve.copy_from(form_curve)
            self_curve.translate(anchor_at.x, anchor_at.y)
            self_curve.adjust_origin()

        if form.shapes_props:
            for point_group_shape in self.point_group_shapes:
                shape_name = point_group_shape.get_name()
                prop_dict = form.shapes_props.get(shape_name)
                if prop_dict is None:
                    continue
                point_group_shape.set_pose_prop_from_dict(prop_dict)
                if not point_group_shape.locked_to_shape:
                    if REL_ABS_ANCHOR_AT in prop_dict:
                        abs_anchor_at = prop_dict[REL_ABS_ANCHOR_AT].copy()
                        abs_anchor_at.translate(self.anchor_at.x, self.anchor_at.y)
                        point_group_shape.move_to(abs_anchor_at.x, abs_anchor_at.y)

        self.update_locked_curve_points()
        self.fit_size_to_include_all()
        #self.move_to(abs_anchor_at.x, abs_anchor_at.y)

    def set_form(self, form_name):
        if form_name not in self.forms:
            return
        form = self.forms[form_name]
        self.set_form_raw(form)

    #wrapper around set_form
    def set_pose(self, pose_name):
        self.set_form(pose_name)

    def set_form_name(self, form_name):
        self.set_form(form_name)

    def get_form_list(self):
        forms = []
        for form_name in sorted(self.forms.keys()):
            forms.append([self.get_form_pixbuf(form_name), form_name])
        return forms

    #wrapper around get_form_list
    def get_pose_list(self, interior_shape=None):
        return self.get_form_list()

    def update_forms_for_point_group(self, point_group_shape, old_translation, old_anchor_at):
        translation_shift = point_group_shape.translation.diff(old_translation)
        anchor_at_shift = point_group_shape.anchor_at.diff(old_anchor_at)

        shape_name = point_group_shape.get_name()
        for form in self.forms.values():
            if not form.shapes_props:
                continue
            prop_dict = form.shapes_props.get(shape_name)
            if not prop_dict:
                continue
            prop_dict["translation"].translate(translation_shift.x, translation_shift.y)
            prop_dict["anchor_at"].translate(anchor_at_shift.x, anchor_at_shift.y)
            prop_dict["width"] = point_group_shape.get_width()
            prop_dict["height"] = point_group_shape.get_height()

    #wrapper around form transition
    def set_pose_transition(self, start_pose, end_pose, value):
        prop_data = dict(start_form=start_pose, end_form=end_pose)
        self.set_prop_value("internal", value, prop_data)

    #wrapper around form transition
    def set_pose_transition(self, start_pose, end_pose, value):
        prop_data = dict(start_form=start_pose, end_form=end_pose)
        self.set_prop_value("internal", value, prop_data)

    def set_prop_value(self, prop_name, value, prop_data=None):
        if prop_name == "internal":
            if "start_form" in prop_data:
                start_form_name = prop_data["start_form"]
                end_form_name = prop_data.get("end_form")
                if end_form_name is None or end_form_name not in self.forms:
                    self.set_form(start_form_name)
                    return

                start_form = self.forms[start_form_name]
                end_form = self.forms[end_form_name]
            else:
                start_form = prop_data["start_form_raw"]
                end_form = prop_data.get("end_form_raw")
            new_width = start_form.width + (end_form.width-start_form.width)*value
            new_height = start_form.height + (end_form.height-start_form.height)*value

            diff_width = new_width - self.width
            diff_height = new_height - self.height

            abs_anchor_at = self.get_abs_anchor_at()

            self.width = new_width
            self.height = new_height
            start_form_curves = start_form.curves
            end_form_curves = end_form.curves

            anchor_at = self.anchor_at.copy()
            anchor_at.scale(1./self.width, 1./self.height)

            minc = min(len(start_form_curves), len(end_form_curves), len(self.curves))
            i = 0
            start_curves = []
            end_curves = []
            while i<minc:
                self_curve = self.curves[i]
                start_form_curve = start_form_curves[i]
                end_form_curve = end_form_curves[i]
                i += 1

                self_curve.set_inbetween(
                    start_form_curve, (start_form.width, start_form.height),
                    end_form_curve, (end_form.width, end_form.height),
                    value, (self.width, self.height))
                self_curve.translate(anchor_at.x, anchor_at.y)

            if start_form.shapes_props and end_form.shapes_props:
                start_shapes_props = start_form.shapes_props
                end_shapes_props = end_form.shapes_props
                for point_group_shape in self.point_group_shapes:
                    shape_name = point_group_shape.get_name()
                    start_prop_dict = start_form.shapes_props.get(shape_name)
                    end_prop_dict = end_form.shapes_props.get(shape_name)
                    if not start_prop_dict or not end_prop_dict:
                        continue
                    point_group_shape.set_transition_pose_prop_from_dict(
                        start_prop_dict, end_prop_dict, frac=value)
                    if not point_group_shape.locked_to_shape and \
                           REL_ABS_ANCHOR_AT in start_prop_dict and \
                           REL_ABS_ANCHOR_AT in end_prop_dict:
                        start_rel_abs_anchor_at = start_prop_dict[REL_ABS_ANCHOR_AT].copy()
                        end_rel_abs_anchor_at = end_prop_dict[REL_ABS_ANCHOR_AT].copy()
                        abs_anchor_at = Point(0, 0)
                        abs_anchor_at.set_inbetween(start_rel_abs_anchor_at, end_rel_abs_anchor_at, value)
                        abs_anchor_at.translate(self.anchor_at.x, self.anchor_at.y)
                        point_group_shape.move_to(abs_anchor_at.x, abs_anchor_at.y)
                self.update_locked_curve_points()
            self.fit_size_to_include_all()
        else:
            Shape.set_prop_value(self, prop_name, value, prop_data)

    def rename_form(self, old_form, new_form):
        if new_form in self.forms: return False
        self.forms[new_form] = self.forms[old_form]
        self.forms[new_form].set_name(new_form)
        del self.forms[old_form]
        return True

    def get_xml_element(self):
        elm = Shape.get_xml_element(self)
        for curve in self.curves:
            elm.append(curve.get_xml_element())
        if not self.show_points:
            elm.attrib["show_points"] = "False"

        for form_name, form in self.forms.items():
            elm.append(form.get_xml_element())

        for point_group_shape in self.point_group_shapes:
            elm.append(point_group_shape.get_xml_element())

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

        for form_elm in elm.findall(CurvesForm.TAG_NAME):
            form = CurvesForm.create_from_xml_element(form_elm)
            shape.forms[form.name] = form

        for point_group_elm in elm.findall(CurvePointGroupShape.TAG_NAME):
            point_group_shape = CurvePointGroupShape.create_from_xml_element(point_group_elm, shape)
            if point_group_shape:
                shape.point_group_shapes.add(point_group_shape)
        shape.assign_params_from_xml_element(elm)
        return shape

    def build_locked_to(self):
        super(CurveShape, self).build_locked_to()
        self.build_interior_locked_to()

    def build_interior_locked_to(self):
        if self.point_group_shapes:
            for point_group_shape in self.point_group_shapes:
                point_group_shape.build_locked_to()
        self.update_locked_curve_points()

    def copy(self, copy_name=False, deep_copy=False, form=None):
        newob = CurveShape(self.anchor_at.copy(), copy_value(self.border_color), self.border_width,
                            copy_value(self.fill_color), self.width, self.height)
        self.copy_into(newob, copy_name)
        for curve in self.curves:
            newob.curves.append(curve.copy())
        if deep_copy:
            newob.forms = copy_value(self.forms)
        newob.show_points = self.show_points
        for point_group_shape in self.point_group_shapes:
            point_group_shape = point_group_shape.copy(copy_name=True, deep_copy=True)
            point_group_shape.set_curve_shape(newob)
            newob.point_group_shapes.add(point_group_shape)
        newob.build_interior_locked_to()
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

        curve.draw_path(ctx)
        ctx.restore()

    def draw_path(self, ctx, for_fill=False):
        paths = []
        for curve in self.curves:
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
        shift = Point(-self.width*outline.left, -self.height*outline.top)
        self.anchor_at.translate(shift.x, shift.y)
        self.move_to(abs_anchor_at.x, abs_anchor_at.y)
        self.set_width(outline.width*self.width, fixed_anchor=False)
        self.set_height(outline.height*self.height, fixed_anchor=False)

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

        for point_group_shape in self.point_group_shapes:
            if point_group_shape.locked_to_shape:
                continue
            point_group_shape.shift_abs_anchor_at(shift)

        self.baked_points = None

    def get_baked_point(self, frac, curve_index=0):
        if self.baked_points is None:
            self.baked_points = dict()
        if self.baked_points.get(curve_index) is None:
            self.baked_points[curve_index] = \
                self.curves[curve_index].get_baked_points(self.width, self.height)
        baked_points = self.baked_points[curve_index]
        if frac<0:
            frac += 1

        if frac>1:
            frac %= 1

        pos = int(baked_points.shape[0]*frac)
        if pos>=baked_points.shape[0]:
            pos=baked_points.shape[0]-1
        x, y = list(baked_points[pos])
        point = self.reverse_transform_point(Point(x*self.width, y*self.height))

        if pos<baked_points.shape[0]-1:
            x, y = list(baked_points[pos+1])
            point2 = self.reverse_transform_point(Point(x*self.width, y*self.height))
            diffp = point2.diff(point)
            angle = diffp.get_angle()
        else:
            angle = 0.
        return point, angle

    def find_point_location(self, point):
        point = point.copy()
        point.scale(1./self.width, 1./self.height)
        tolerance = 5./max(self.width, self.height)
        for curve_index in range(len(self.curves)):
            curve = self.curves[curve_index]
            found = curve.get_closest_control_point(point, self.width, self.height, tolerance)
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

        for point_group_shape in self.point_group_shapes:
            curve_point_group = point_group_shape.curve_point_group
            curve_point_group.shift(
                    curve_index=curve_index,
                    from_point_index=bezier_point_index,
                    point_index_shift=1)
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
        bezier_points_count = len(prev_curve.bezier_points)

        if prev_curve.closed:
            prev_curve.closed = False
            prev_curve.add_bezier_points(prev_curve.bezier_points[:bezier_point_index+1])
            prev_curve.remove_bezier_point_indices(0, bezier_point_index)
            prev_curve.origin.copy_from(prev_curve.bezier_points[0].dest)
            prev_curve.remove_bezier_point_index(0)

            for point_group_shape in self.point_group_shapes:
                curve_point_group = point_group_shape.curve_point_group
                curve_point_group.shift(
                        curve_index=curve_index,
                        from_point_index=0, to_point_index=bezier_point_index+1,
                        point_index_shift=bezier_points_count)
                curve_point_group.shift(
                        curve_index=curve_index,
                        from_point_index=0,
                        point_index_shift=-bezier_point_index-1)
        else:
            bezier_point = prev_curve.bezier_points[bezier_point_index]
            new_curve = Curve(origin=bezier_point.dest.copy(),
                              bezier_points=prev_curve.bezier_points[bezier_point_index+1:])
            prev_curve.remove_bezier_point_indices(bezier_point_index+1, len(prev_curve.bezier_points))
            self.curves.insert(curve_index+1, new_curve)

            for point_group_shape in self.point_group_shapes:
                curve_point_group = point_group_shape.curve_point_group
                curve_point_group.shift(
                        curve_index=curve_index,
                        from_point_index=bezier_point_index+1,
                        curve_index_shift=1)
                curve_point_group.shift(
                        curve_index=curve_index+1,
                        from_point_index=bezier_point_index+1,
                        point_index_shift=-bezier_point_index-1)

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
            for point_group_shape in self.point_group_shapes:
                point_group_shape.curve_point_group.reverse_shift(
                    curve_index=curve_index_2,
                    point_index_max=len(curve_2.bezier_points)-1)

        if is_start_1:#swap curves
            curve_1, curve_2 = curve_2, curve_1
            curve_index_1, curve_index_2 = curve_index_2, curve_index_1

        #curve_2 get attached at the end of curve_1
        curve_1.bezier_points[-1].dest.x = (curve_1.bezier_points[-1].dest.x +  curve_2.origin.x)*.5
        curve_1.bezier_points[-1].dest.y = (curve_1.bezier_points[-1].dest.y +  curve_2.origin.y)*.5

        for point_group_shape in self.point_group_shapes:
            point_group_shape.curve_point_group.shift(
                curve_index=curve_index_2,
                point_index_shift=len(curve_1.bezier_points))
        for point_group_shape in self.point_group_shapes:
            point_group_shape.curve_point_group.shift(
                curve_index=curve_index_2,
                curve_index_shift=curve_index_1-curve_index_2)

        curve_1.add_bezier_points(curve_2.bezier_points)
        del self.curves[curve_index_2]

        return True

    def extend_point(self, curve_index, is_start, point_index):
        if curve_index>=len(self.curves): return False
        curve = self.curves[curve_index]
        #if curve.closed: return False

        if is_start:
            curve.insert_point_at(0, t=0.0)
        else:
            curve.insert_point_at(point_index, t=1.0)
        return True

    def delete_point_group_curve(self, curve_index):
        for point_group_shape in self.point_group_shapes:
            point_group_shape.curve_point_group.delete_curve(curve_index)
        self.cleanup_point_groups()

    def delete_point_group_point(self, curve_index, point_index):
        for point_group_shape in self.point_group_shapes:
            point_group_shape.curve_point_group.delete_point_index(curve_index, point_index)
        self.cleanup_point_groups()

    def cleanup_point_groups(self):
        i = 0
        while i <len(self.point_group_shapes):
            point_group_shape = self.point_group_shapes.get_at_index(i)
            point_group = point_group_shape.curve_point_group
            if len(point_group.points)<1:
                self.point_group_shapes.remove(point_group_shape)
            else:
                i += 1

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
                self.delete_point_group_point(curve_index, 0)
                if curve.closed:
                    curve.bezier_points[-1].dest.copy_from(curve.origin)
                    curve.update_bezier_point_index(-1)#
            elif bezier_point_index == len(curve.bezier_points)-1:
                if curve.closed and curve.bezier_points:
                    curve.origin.copy_from(curve.bezier_points[0].dest)
                    curve.bezier_points[-1].dest.copy_from(curve.origin)
                    curve.update_bezier_point_index(-1)#
                    curve.remove_bezier_point_index(0)
                    self.delete_point_group_point(curve_index, 0)
                else:
                    curve.remove_bezier_point_index(-1)
                    self.delete_point_group_point(curve_index, len(curve.bezier_points)-1)
            else:
                if break_allowed:
                    new_curve = Curve(origin=curve.bezier_points[bezier_point_index].dest.copy())
                    new_curve.add_bezier_points(curve.bezier_points[bezier_point_index+1:])
                    curve.remove_bezier_point_indices(
                        bezier_point_index+1, len(curve.bezier_points))
                    self.curves.insert(curve_index+1, new_curve)
                curve.remove_bezier_point_index(bezier_point_index)
                self.delete_point_group_point(curve_index, bezier_point_index)

            if len(curve.bezier_points)<3:
                curve.closed = False
            if len(self.curves)>1:
                if (len(curve.bezier_points)<=1 and curve.closed) or len(curve.bezier_points)==0:
                    del self.curves[curve_index]
                    self.delete_point_group_curve(curve_index)
        elif len(self.curves)>1:
            del self.curves[curve_index]
            self.delete_point_group_curve(curve_index)
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
            curve.origin.copy_from(self._transform_point_from_shape(shape, curve.origin))
            for i in range(len(curve.bezier_points)):
                bp = curve.bezier_points[i]
                bp.control_1.copy_from(self._transform_point_from_shape(shape, bp.control_1))
                bp.control_2.copy_from(self._transform_point_from_shape(shape, bp.control_2))
                bp.dest.copy_from(self._transform_point_from_shape(shape, bp.dest))
            self.curves.append(curve)
        return True
