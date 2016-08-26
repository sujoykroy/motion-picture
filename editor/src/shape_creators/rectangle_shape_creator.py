from ..commons import *
from ..shapes import RectangleShape, RectEditBox

class RectangleShapeCreator(object):
    def __init__(self, point):
        self.shape = RectangleShape(Point(0, 0), Color(0,0,0,1), 5, Color(1,1,1,0), 1, 1, 0)
        self.edit_boxes = []
        self.edit_boxes.append(RectEditBox(Point(0, 0), width=5, height=5, is_percent = False))
        self.edit_boxes.append(RectEditBox(Point(0, 0), width=5, height=5, is_percent = False))

    def set_relative_to(self, multi_shape):
        self.shape.move_to(multi_shape.translation.x, multi_shape.translation.y)
        for edit_box in self.edit_boxes:
            edit_box.parent_shape = multi_shape

    def begin_movement(self, point):
        self.do_movement(point, point)

    def do_movement (self, start_point, end_point):
        diff_point = end_point.diff(start_point)
        self.shape.set_width(abs(diff_point.x))
        self.shape.set_height(abs(diff_point.y))
        self.shape.anchor_at.x = abs(diff_point.x)*.5
        self.shape.anchor_at.y = abs(diff_point.y)*.5

        if diff_point.x>0:
            mx = start_point.x+self.shape.anchor_at.x
        else:
            mx = end_point.x+self.shape.anchor_at.x

        if diff_point.y>0:
            my = start_point.y+self.shape.anchor_at.y
        else:
            my = end_point.y+self.shape.anchor_at.y

        self.shape.move_to(mx, my)

        self.edit_boxes[0].set_point(start_point)
        self.edit_boxes[1].set_point(end_point)

        for edit_box in self.edit_boxes:
            edit_box.reposition(None)

    def get_shape(self):
        return self.shape

    def draw(self, ctx):
        for edit_box in self.edit_boxes:
            ctx.save()
            edit_box.draw(ctx)
            ctx.restore()

    def end_movement(self):
        return True

    def close_down(self):
        pass
