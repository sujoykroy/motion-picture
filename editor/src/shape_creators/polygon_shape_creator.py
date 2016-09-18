from ..commons import *
from ..shapes import PolygonShape, OvalEditBox

class PolygonShapeCreator(object):
    def __init__(self, point):
        self.shape = PolygonShape(Point(0, 0), Color(0,0,0,1), 1, Color(1,1,1,0), 1, 1)
        self.polygon = None
        self.point = None
        self.shape.move_to(point.x, point.y)

        self.edit_boxes = []
        ctc = Color(1,1,0,1)
        self.edit_boxes.append(OvalEditBox(point.copy(), radius=5, is_percent = True, fill_color=ctc))

    def set_relative_to(self, multi_shape):
        self.shape.move_to(multi_shape.translation.x, multi_shape.translation.y)
        for edit_box in self.edit_boxes:
            edit_box.parent_shape = multi_shape
        rect = self.shape.get_outline(0)

        for edit_box in self.edit_boxes:
            edit_box.reposition(rect)

    def begin_movement(self, point):
        self.do_movement(point, point)

    def do_movement (self, start_point, end_point):
        if self.polygon is None:
            self.polygon = Polygon(points=[self.shape.transform_point(end_point)])
            self.shape.add_polygon(self.polygon)
            return
        if self.point is None:
            return
        self.edit_boxes[0].set_point(end_point)

        rect = self.shape.get_outline(0)
        for edit_box in self.edit_boxes:
            edit_box.reposition(rect)

        self.point.copy_from(end_point)

    def get_shape(self):
        return self.shape

    def draw(self, ctx):
        for edit_box in self.edit_boxes:
            edit_box.draw_edit_box(ctx)

    def end_movement(self):
        if self.point is None:
            last_point = self.polygon.points[0]
        else:
            last_point = self.point
        self.point = last_point.copy()
        self.polygon.add_point(self.point)
        return False

    def close_down(self):
        self.shape.fit_size_to_include_all()

        del self.polygon.points[-1]
        dx = self.polygon.points[-1].x - self.polygon.points[0].x
        dy = self.polygon.points[-1].y - self.polygon.points[0].y

        dx *= self.shape.width
        dy *= self.shape.height

        spread = 5
        if abs(dx)<spread and abs(dy)<spread:
            self.polygon.set_closed(True)
            self.polygon.points[-1].copy_from(self.polygon.points[0])
        self.shape.fit_size_to_include_all()

        self.shape.anchor_at.x = self.shape.width*.5
        self.shape.anchor_at.y = self.shape.height*.5
