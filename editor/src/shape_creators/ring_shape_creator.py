from ..commons import *
from ..shapes import RingShape, RectEditBox
from .rectangle_shape_creator import RectangleShapeCreator

class RingShapeCreator(RectangleShapeCreator):
    def __init__(self, point):
        self.shape = RingShape(Point(0, 0), Color(0,0,0,1), 5, Color(1,1,1,0), 1, 1, 300, .2)
        self.edit_boxes = []
        self.edit_boxes.append(RectEditBox(Point(0, 0), width=5, height=5, is_percent = False))
        self.edit_boxes.append(RectEditBox(Point(0, 0), width=5, height=5, is_percent = False))
