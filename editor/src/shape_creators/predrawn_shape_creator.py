from ..commons import *
from ..shapes import RectEditBox
from rectangle_shape_creator import RectangleShapeCreator

class PredrawnShapeCreator(RectangleShapeCreator):
    def __init__(self, point, document):
        self.shape = document.main_multi_shape.copy()
        self.edit_boxes = []
        self.edit_boxes.append(RectEditBox(Point(0, 0), width=5, height=5, is_percent = False))
        self.edit_boxes.append(RectEditBox(Point(0, 0), width=5, height=5, is_percent = False))

    def begin_movement(self, point):
        wh = self.shape.transform_point(Point(1, 1))
        self.shape.set_width(wh.x)
        self.shape.set_height(wh.y)
        RectangleShapeCreator.do_movement(self, point, point)
