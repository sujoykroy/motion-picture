from ..commons import *
from ..shapes import RectEditBox, MultiShape
from .rectangle_shape_creator import RectangleShapeCreator

class PredrawnShapeCreator(RectangleShapeCreator):
    def __init__(self, point, document):
        if len(document.main_multi_shape.shapes)> 1:
            self.shape = document.main_multi_shape.copy()
        else:
            self.shape = document.main_multi_shape.shapes.get_at_index(0).copy()
        self.shape.anchor_at.x = 0
        self.shape.anchor_at.y = 0

        self.init_shape = self.shape.copy()

        self.edit_boxes = []
        self.edit_boxes.append(RectEditBox(Point(0, 0), width=5, height=5, is_percent = False))
        self.edit_boxes.append(RectEditBox(Point(0, 0), width=5, height=5, is_percent = False))

    def do_movement (self, start_point, end_point):
        self.edit_boxes[0].set_point(start_point)
        self.edit_boxes[1].set_point(end_point)

        for edit_box in self.edit_boxes:
            edit_box.reposition(None)

        diff_point = end_point.diff(start_point)
        if abs(diff_point.x) ==0:
            diff_point.x = 1.
        if abs(diff_point.y) ==0:
            diff_point.y = 1.

        if isinstance(self.shape, MultiShape):
            self.shape.post_scale_x = self.init_shape.post_scale_x*\
                        (abs(diff_point.x)/self.init_shape.width)
            self.shape.post_scale_y = self.init_shape.post_scale_y*\
                    (abs(diff_point.y)/self.init_shape.height)
        else:
            self.shape.set_width(abs(diff_point.x))
            self.shape.set_height(abs(diff_point.y))

        if diff_point.x>0:
            mx = start_point.x+self.shape.anchor_at.x
        else:
            mx = end_point.x+self.shape.anchor_at.x

        if diff_point.y>0:
            my = start_point.y+self.shape.anchor_at.y
        else:
            my = end_point.y+self.shape.anchor_at.y

        self.shape.move_to(mx, my)
