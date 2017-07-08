from ..commons import *
from shape import Shape
from rectangle_shape import RectangleShape

class CurvePointGroupShape(RectangleShape):
    TYPE_NAME = "curve_point_group_shape"

    def __init__(self, anchor_at=Point(0,0), border_color="00ff00",
                       border_width=1, fill_color=None, width=1, height=1, corner_radius=0,
                       curve_shape=None, curve_point_group=None):
        RectangleShape.__init__(self, anchor_at, border_color, border_width,
                                        fill_color, width, height, corner_radius)
        self.curve_point_group = curve_point_group
        self.parent_shape = curve_shape

    def copy(self, copy_name=False, deep_copy=False):
        newob = CurvePointGroupShape(
                        curve_shape=self.parent_shape,
                        curve_point_group=self.curve_point_group.copy())
        self.copy_into(newob, copy_name, all_fields=True)
        return newob

    def get_xml_element(self):
        elm = super(CurvePointGroupShape, self).get_xml_element()
        elm.append(self.curve_point_group.get_xml_element())
        return elm

    @classmethod
    def create_from_xml_element(cls, elm, curve_shape):
        point_group_elm = elm.find(CurvePointGroup.TAG_NAME)
        if not point_group_elm:
            return None
        point_group = CurvePointGroup.create_from_xml_element(point_group_elm)

        arr = Shape.get_params_array_from_xml_element(elm)
        arr.append(float(elm.attrib.get("corner_radius", 0)))
        arr.append(curve_shape)
        arr.append(point_group)

        shape = cls(*arr)
        shape.assign_params_from_xml_element(elm)
        return shape

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
        self.update()

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
        if not self.parent_shape.point_group_should_update:
            return
        curve_sx = 1./self.parent_shape.get_width()
        curve_sy = 1./self.parent_shape.get_height()
        for curve_point in self.curve_point_group.points:
            point = curve_point.position.copy()
            point = self.reverse_transform_point(point)
            point.scale(curve_sx, curve_sy)
            curve = self.parent_shape.curves[curve_point.curve_index]
            curve_point.get_point(curve).copy_from(point)
        self.curve_point_group.update_closed_curves(self.parent_shape.curves)
