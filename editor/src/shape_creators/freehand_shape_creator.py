from ..commons import *
from ..shapes import PolygonShape, OvalEditBox
from ..shapes import CurveShape
from ..settings import config

class FreehandShapeCreator(object):
    def __init__(self, point, curve_shape=None):
        if curve_shape is None:
            self.shape = CurveShape(Point(0, 0), Color(0,0,0,1),
                    config.DEFAULT_BORDER_WIDTH, Color(1,1,1,0), 1, 1)
            self.shape.move_to(point.x, point.y)
            self.new_shape = True
        else:
            self.shape = curve_shape
            self.new_shape = False
        self.shape.show_points = False
        self.edit_boxes = []
        ctc = Color(1,1,0,1)
        self.edit_boxes.append(OvalEditBox(point.copy(), radius=5, is_percent = True, fill_color=ctc))
        self.can_move= False

    def set_relative_to(self, multi_shape):
        if self.new_shape:
            self.shape.move_to(multi_shape.translation.x, multi_shape.translation.y)
        for edit_box in self.edit_boxes:
            edit_box.parent_shape = multi_shape
        rect = self.shape.get_outline(0)

        for edit_box in self.edit_boxes:
            edit_box.reposition(rect)

    def begin_movement(self, point):
        origin = point.copy()
        origin.scale(1./self.shape.width, 1./self.shape.height)
        self.curve = Curve(origin=origin, bezier_points=[])
        self.shape.curves.append(self.curve)
        self.can_move = True
        self.do_movement(point, point)

    def do_movement (self, start_point, end_point):
        if not self.can_move: return
        trans_end_point = self.shape.transform_point(end_point)
        if not self.curve.bezier_points or \
            trans_end_point.distance(self.curve.bezier_points[-1].dest)> 1:
            trans_end_point.scale(1./self.shape.width, 1./self.shape.height)
            bzp = BezierPoint(control_1=trans_end_point.copy(), control_2=trans_end_point.copy(),
                              dest=trans_end_point.copy())
            if self.curve.bezier_points:
                bzp.align_straight_with(self.curve.bezier_points[-1].dest)
            else:
                bzp.align_straight_with(self.curve.origin)
            self.curve.add_bezier_point(bzp)
            self.edit_boxes[0].set_point(end_point)

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
        if self.curve and len(self.curve.bezier_points)==1:
            del self.shape.curves[-1]
        return False

    def close_down(self):
        if self.curve and len(self.curve.bezier_points)==1:
            del self.shape.curves[-1]
        self.shape.fit_size_to_include_all()
        self.shape.anchor_at.x = self.shape.width*.5
        self.shape.anchor_at.y = self.shape.height*.5
