from ..commons import *
from ..shapes import TextShape, RectEditBox
from .rectangle_shape_creator import RectangleShapeCreator

class TextShapeCreator(RectangleShapeCreator):
    def __init__(self, point):
        self.shape = TextShape(Point(0, 0), Color(0,0,0,1), 5, Color(1,1,1,0), 1, 1, 0)
        self.edit_boxes = []
        self.edit_boxes.append(RectEditBox(Point(0, 0), width=5, height=5, is_percent = False))
        self.edit_boxes.append(RectEditBox(Point(0, 0), width=5, height=5, is_percent = False))
