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

    def get_point_group(self):
        return self.curve_point_group

    def update(self):
        self.reset_transformations()
        self.anchor_at.assign(0, 0)

        w = self.curve_shape.get_width()
        h = self.curve_shape.get_height()
        refix_anchor = (len(self.curve_rel_points) != 0)
        points = []
        del self.curve_rel_points [:]

        for curve_point in self.curve_point_group.points:
            if curve_point.curve_index>=len(self.curve_shape.curves):
                continue
            curve = self.curve_shape.curves[curve_point.curve_index]
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

            curve_rel_point = CurveRelPoint(curve_point=curve_point, rel=point.copy())
            curve_rel_point.rel.scale(w, h)
            self.curve_rel_points.append(curve_rel_point)
            points.append(curve_rel_point.rel)

        outline = Polygon(points).get_outline()
        if outline is None:
            return

        self.move_to(outline.left, outline.top)
        self.width = outline.width
        self.height = outline.height
        if self.curve_point_group.abs_anchor_at is None:
            anchor_at = self.reverse_transform_point(Point(self.width*.5, self.height*.5))
            self.curve_point_group.set_abs_anchor_at(anchor_at.x, anchor_at.y)

        sx = 1./self.width
        sy = 1./self.height

        for curve_rel_point in self.curve_rel_points:
            curve_rel_point.rel.translate(-outline.left, -outline.top)
            curve_rel_point.rel.scale(sx, sy)

        anchor_at = self.transform_point(self.curve_point_group.abs_anchor_at)
        super(CurvePointGroupShape, self).set_anchor_at(anchor_at.x, anchor_at.y)

    def set_anchor_x(self, x):
        super(CurvePointGroupShape, self).set_anchor_x(x)
        self.update_group_anchor()

    def set_anchor_y(self, y):
        super(CurvePointGroupShape, self).set_anchor_y(y)
        self.update_group_anchor()

    def update_group_anchor(self):
        anchor_at = self.get_abs_anchor_at()
        self.curve_point_group.set_abs_anchor_at(anchor_at.x, anchor_at.y)

    def translate_anchor(self, dx, dy):
        self.curve_point_group.abs_anchor_at.translate(dx, dy)

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

        self.curve_point_group.update_closed_curves(self.curve_shape.curves)