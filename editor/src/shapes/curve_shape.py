from ..commons import *
from shape import Shape
from xml.etree.ElementTree import Element as XmlElement

class CurveShape(Shape):
    TYPE_NAME = "curve_shape"
    FORM_TAG_NAME = "form"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height):
        Shape.__init__(self, anchor_at, border_color, border_width, fill_color, width, height)
        self.curves = []
        self.forms = dict()

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

        for form_name, form in self.forms.items():
            form_elm = XmlElement(self.FORM_TAG_NAME)
            form_elm.attrib["name"] = form_name
            form_elm.attrib["width"] = "{0}".format(form["width"])
            form_elm.attrib["height"] = "{0}".format(form["height"])
            for curve in form["curves"]:
                form_elm.append(curve.get_xml_element())
            elm.append(form_elm)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        arr = Shape.get_params_array_from_xml_element(elm)
        shape = cls(*arr)
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

        shape.assign_params_from_xml_element(elm)
        return shape

    def copy(self, copy_name=False):
        newob = CurveShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                            self.fill_color.copy(), self.width, self.height)
        self.copy_into(newob, copy_name)
        for curve in self.curves:
            newob.curves.append(curve.copy())
        return newob

    def is_empty(self):
        return len(self.curves) == 0

    def add_curve(self, curve):
        self.curves.append(curve)
        self.fit_size_to_include_all()

    def _draw_curve(self, ctx, curve):
        ctx.save()
        ctx.scale(self.width, self.height)
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
            found = curve.get_closest_control_point(point)
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
