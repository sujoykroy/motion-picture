from ..commons import *
from ..shapes import CameraShape, RectEditBox
from rectangle_shape_creator import RectangleShapeCreator
from ..settings import config

class CameraShapeCreator(RectangleShapeCreator):
    def __init__(self, point):
        self.shape = CameraShape(Point(0, 0), Color(0,0,0,1),
                        config.DEFAULT_BORDER_WIDTH, Color(1,1,1,0), 1, 1,
                        aspect_ratio="1:1", eye_type=CameraShape.EYE_TYPE_RECTANGLE)
        self.edit_boxes = []
        self.edit_boxes.append(RectEditBox(Point(0, 0), width=5, height=5, is_percent = False))
        self.edit_boxes.append(RectEditBox(Point(0, 0), width=5, height=5, is_percent = False))
