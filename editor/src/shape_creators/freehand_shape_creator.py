from ..commons import *
from ..shapes import PolygonShape, OvalEditBox

class FreehandShapeCreator(object):
    def __init__(self, point):
        self.shape = PolygonShape(Point(0, 0), Color(0,0,0,1), 10, Color(1,1,1,0), 1, 1)
        self.shape.move_to(point.x, point.y)

        self.edit_boxes = []
        ctc = Color(1,1,0,1)
        self.edit_boxes.append(OvalEditBox(point.copy(), radius=5, is_percent = True, fill_color=ctc))
        self.can_move= False

    def set_relative_to(self, multi_shape):
        self.shape.move_to(multi_shape.translation.x, multi_shape.translation.y)
        for edit_box in self.edit_boxes:
            edit_box.parent_shape = multi_shape
        rect = self.shape.get_outline(0)

        for edit_box in self.edit_boxes:
            edit_box.reposition(rect)

    def begin_movement(self, point):
        self.polygon = Polygon(points=[])
        self.shape.polygons.append(self.polygon)
        self.can_move = True
        self.do_movement(point, point)

    def do_movement (self, start_point, end_point):
        if not self.can_move: return
        rel_end_point = end_point
        scaled_rel_end_point = rel_end_point.copy()
        scaled_rel_end_point.scale(self.shape.width, self.shape.height)

        if not self.polygon.points or scaled_rel_end_point.distance(self.polygon.points[-1])> 1:
            self.polygon.add_point(scaled_rel_end_point.copy())
            self.edit_boxes[0].set_point(scaled_rel_end_point)

        rect = self.shape.get_outline(0)
        for edit_box in self.edit_boxes:
            edit_box.reposition(rect)

    def get_shape(self):
        return self.shape

    def draw(self, ctx):
        for edit_box in self.edit_boxes:
            edit_box.draw(ctx)

    def end_movement(self):
        self.can_move = False
        return False

    def close_down(self):
        self.shape.fit_size_to_include_all()
        self.shape.anchor_at.x = self.shape.width*.5
        self.shape.anchor_at.y = self.shape.height*.5
