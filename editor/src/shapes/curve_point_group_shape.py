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
        self.curve_shape = curve_shape
        self.parent_shape = curve_shape
        self.curve_rel_points = []
        self.update()

    def copy(self, copy_name=False, deep_copy=False):
        newob = CurvePointGroupShape(self.curve_shape, self.curve_point_group)
        self.copy_into(newob, copy_name, all_fields=True)
        return newob

    def update(self):
        w = self.curve_shape.get_width()
        h = self.curve_shape.get_height()

        points = []
        del self.curve_rel_points [:]

        for curve_point in self.curve_point_group.points:
            curve = self.curve_shape.curves[curve_point.curve_index]
            bezier_point = curve.bezier_points[curve_point.point_index]
            if curve_point.point_type == CurvePoint.POINT_TYPE_DEST:
                point = bezier_point.dest
            elif curve_point.point_type == CurvePoint.POINT_TYPE_CONTROL_1:
                point = bezier_point.control_1
            elif curve_point.point_type == CurvePoint.POINT_TYPE_CONTROL_2:
                point = bezier_point.control_2

            curve_rel_point = CurveRelPoint(curve_point=curve_point, rel=point.copy())
            curve_rel_point.rel.scale(w, h)
            self.curve_rel_points.append(curve_rel_point)
            points.append(curve_rel_point.rel)

        outline = Polygon(points).get_outline()

        self.move_to(outline.left, outline.top)
        self.width = outline.width
        self.height = outline.height
        self.anchor_at.assign(self.width*.5, self.height*.5)

        sx = 1./self.width
        sy = 1./self.height
        for curve_rel_point in self.curve_rel_points:
            curve_rel_point.rel.translate(-outline.left, -outline.top)
            curve_rel_point.rel.scale(sx, sy)

    def update_rel_points(self):
        curve_sx = 1./self.curve_shape.get_width()
        curve_sy = 1./self.curve_shape.get_height()
        for curve_rel_point in self.curve_rel_points:
            point = curve_rel_point.rel.copy()
            point.scale(self.width, self.height)
            point = self.reverse_transform_point(point)
            point.scale(curve_sx, curve_sy)
            curve_point = curve_rel_point.curve_point
            curve = self.curve_shape.curves[curve_point.curve_index]
            curve_point.get_point(curve).copy_from(point)
