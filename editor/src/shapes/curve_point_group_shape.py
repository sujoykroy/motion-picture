from ..commons import *
from shape import Shape
from rectangle_shape import RectangleShape

class CurvePointGroupShape(RectangleShape):
    TYPE_NAME = "curve_point_group_shape"

    def __init__(self, anchor_at=Point(0,0), border_color="00ff00",
                       border_width=1, fill_color=None, width=1, height=1, corner_radius=0,
                       curve_shape=None, curve_point_group=None):
        RectangleShape.__init__(self, anchor_at.copy(), border_color, border_width,
                                        fill_color, width, height, corner_radius)
        self.curve_point_group = curve_point_group
        self.parent_shape = curve_shape
        self.show_anchor = True

    def set_curve_shape(self, curve_shape):
        self.parent_shape = curve_shape

    def can_resize(self):
        return len(self.curve_point_group.points)>1

    def can_rotate(self):
        return len(self.curve_point_group.points)>1

    def can_change_anchor(self):
        return self.show_anchor and len(self.curve_point_group.points)>1

    def copy(self, copy_name=False, deep_copy=False):
        newob = CurvePointGroupShape(
                        anchor_at=self.anchor_at.copy(),
                        border_color=copy_value(self.border_color),
                        border_width=self.border_width,
                        fill_color=copy_value(self.fill_color),
                        width=self.width, height=self.height,
                        corner_radius=self.corner_radius,
                        curve_shape=self.parent_shape,
                        curve_point_group=self.curve_point_group.copy())
        self.copy_into(newob, copy_name, all_fields=deep_copy)
        return newob

    def get_xml_element(self):
        elm = super(CurvePointGroupShape, self).get_xml_element()
        elm.append(self.curve_point_group.get_xml_element())
        if not self.show_anchor:
            elm.attrib["show_anchor"] = "0"
        return elm

    @classmethod
    def create_from_xml_element(cls, elm, curve_shape):
        point_group_elm = elm.find(CurvePointGroup.TAG_NAME)
        if not point_group_elm:
            return None
        point_group = CurvePointGroup.create_from_xml_element(
                point_group_elm, curve_shape.curves)

        arr = Shape.get_params_array_from_xml_element(elm)
        arr.append(float(elm.attrib.get("corner_radius", 0)))
        arr.append(curve_shape)
        arr.append(point_group)

        shape = cls(*arr)
        shape.assign_params_from_xml_element(elm)

        shape.show_anchor = bool(int(elm.attrib.get("show_anchor", 1)))
        return shape

    def add_curve_points(self, curve_points):
        count = 0
        for curve_point in curve_points:
            if self.curve_point_group.add_point(curve_point):
                count += 1
                point = curve_point.get_point(self.parent_shape.curves).copy()
                point.scale(self.parent_shape.width, self.parent_shape.height)
                point = self.transform_point(point)
                curve_point.position.copy_from(point)
        if count>0:
            self.fit_size_to_include_all()
        return count>0

    def remove_curve_points(self, curve_points):
        count = 0
        for curve_point in curve_points:
            if self.curve_point_group.remove_point(curve_point):
                count += 1
        if count>0:
            self.fit_size_to_include_all()
        return count>0

    def fit_size_to_include_all(self):
        positions = []
        for curve_point in self.curve_point_group.points:
            positions.append(curve_point.position)

        outline = Polygon(positions).get_outline()
        if outline is None:
            return

        abs_anchor_at = self.get_abs_anchor_at()
        self.width = outline.width
        self.height = outline.height
        self.anchor_at.translate(-outline.left, -outline.top)
        self.move_to(abs_anchor_at.x, abs_anchor_at.y)

        for curve_point in self.curve_point_group.points:
            curve_point.position.translate(-outline.left, -outline.top)

    def build(self):
        w = self.parent_shape.get_width()
        h = self.parent_shape.get_height()

        points = []
        points_positions = []
        for curve_point in self.curve_point_group.points:
            point = curve_point.get_point(self.parent_shape.curves)
            if not point:
                continue
            point = point.copy()
            point.scale(w, h)
            point = self.transform_locked_shape_point(point)
            points_positions.append((point, curve_point.position))
            points.append(point)

        outline = Polygon(points).get_outline()
        if outline is None:
            if len(points) == 1:
                w = h = 5.
                outline = Rect(left=points[0].x-w*.5, top=points[0].y-h*.5,
                               width=w, height=h)
            else:
                return

        old_translation = self.translation.copy()

        self.anchor_at.assign(0, 0)
        self.move_to(outline.left, outline.top)
        self.width = outline.width
        self.height = outline.height
        anchor_at = Point(self.width*.5, self.height*.5)
        self.anchor_at.copy_from(anchor_at)
        for point, position in points_positions:
            point = self.transform_point(point)
            position.copy_from(point)

        if self.locked_shapes:
            shift = old_translation.diff(self.translation)
            for locked_shape in self.locked_shapes:
                if isinstance(locked_shape, CurvePointGroupShape):
                    locked_shape.shift_abs_anchor_at(shift)

        self.update_curve_points()

    def update_curve_points(self, update_locked_shape=True):
        curve_sx = 1./self.parent_shape.get_width()
        curve_sy = 1./self.parent_shape.get_height()
        for curve_point in self.curve_point_group.points:
            point = curve_point.position.copy()
            locked_to_shape = self.locked_to_shape
            point = self.reverse_transform_locked_shape_point(point)
            point.scale(curve_sx, curve_sy)
            orig_point = curve_point.get_point(self.parent_shape.curves)
            if orig_point:
                orig_point.copy_from(point)
            curve_point.update_original(point, self.parent_shape.curves)

        if update_locked_shape:
            if self.locked_shapes:
                for locked_shape in self.locked_shapes:
                    if isinstance(locked_shape, CurvePointGroupShape):
                        locked_shape.update_curve_points()

    def update_to_locked_shape(self):
        self.update_curve_points(update_locked_shape=False)
