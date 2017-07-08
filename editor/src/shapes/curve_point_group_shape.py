from ..commons import *
from shape import Shape
from rectangle_shape import RectangleShape

class CurveRelPoint(object):
    def __init__(self, curve_point, rel):
        self.curve_point = curve_point
        self.rel = rel

class CurvePointGroupShape(RectangleShape):
    TYPE_NAME = "curve_point_group_shape"

    def __init__(self, curve_shape, curve_point_group):
        RectangleShape.__init__(self, anchor_at=Point(0,0), border_color="00ff00",
                                      border_width=1, fill_color=None, width=1, height=1, corner_radius=0)
        self.curve_point_group = curve_point_group
        self.parent_shape = curve_shape

    def copy(self, copy_name=False, deep_copy=False):
        newob = CurvePointGroupShape(self.parent_shape, self.curve_point_group.copy())
        self.copy_into(newob, copy_name, all_fields=True)
        return newob

    def build(self):
        w = self.parent_shape.get_width()
        h = self.parent_shape.get_height()

        points = []
        points_positions = []
        for curve_point in self.curve_point_group.points:
            if curve_point.curve_index>=len(self.parent_shape.curves):
                continue
            curve = self.parent_shape.curves[curve_point.curve_index]
            if curve_point.point_index>= len(curve.bezier_points):
                continue
            bezier_point = curve.bezier_points[curve_point.point_index]
            if curve_point.point_type == CurvePoint.POINT_TYPE_DEST:
                point = bezier_point.dest
            elif curve_point.point_type == CurvePoint.POINT_TYPE_CONTROL_1:
                point = bezier_point.control_1
            elif curve_point.point_type == CurvePoint.POINT_TYPE_CONTROL_2:
                point = bezier_point.control_2
            elif curve_point.point_type == CurvePoint.POINT_TYPE_ORIGIN:
                point = curve.origin

            point = point.copy()
            point.scale(w, h)
            points_positions.append((point, curve_point.position))
            points.append(point)

        outline = Polygon(points).get_outline()
        if outline is None:
            return

        self.anchor_at.assign(0, 0)
        self.move_to(outline.left, outline.top, update=False)
        self.width = outline.width
        self.height = outline.height
        anchor_at = Point(self.width*.5, self.height*.5)
        self.anchor_at.copy_from(anchor_at)

        for point, position in points_positions:
            point = self.transform_point(point)
            position.copy_from(point)

    def set_width(self, value, fixed_anchor=False):
        super(CurvePointGroupShape, self).set_width(value, fixed_anchor)
        self.update()

    def set_height(self, value, fixed_anchor=False):
        super(CurvePointGroupShape, self).set_height(value, fixed_anchor)
        self.update()

    def set_angle(self, value):
        super(CurvePointGroupShape, self).set_angle(value)
        self.update()

    def move_to(self, x, y, update=True):
        super(CurvePointGroupShape, self).move_to(x, y)
        if update:
            self.update()

    def update(self):
        curve_sx = 1./self.parent_shape.get_width()
        curve_sy = 1./self.parent_shape.get_height()
        for curve_point in self.curve_point_group.points:
            point = curve_point.position.copy()
            point = self.reverse_transform_point(point)
            point.scale(curve_sx, curve_sy)
            curve = self.parent_shape.curves[curve_point.curve_index]
            curve_point.get_point(curve).copy_from(point)
        self.curve_point_group.update_closed_curves(self.parent_shape.curves)
