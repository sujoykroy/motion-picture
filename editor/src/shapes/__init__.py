from shape import Shape
from shape_list import ShapeList
from rectangle_shape import RectangleShape
from oval_shape import OvalShape
from curve_shape import CurveShape
from polygon_shape import PolygonShape
from multi_shape import MultiShape
from image_shape import ImageShape
from multi_selection_shape import MultiSelectionShape
from edit_shapes import *

def get_hierarchy_names(shape):
    names = [shape.get_name()]
    prev_shape = shape
    while prev_shape.parent_shape:
        prev_shape = prev_shape.parent_shape
        if isinstance(prev_shape, MultiSelectionShape): continue
        names.insert(0, prev_shape.get_name())
    return names[1:]#top shape is document area box, exclude it

def get_shape_at_hierarchy(multi_shape, names):
    shape = None
    for i in range(len(names)):
        name = names[i]
        if i == 0:
             if multi_shape.get_name() == name:
                shape = multi_shape
             else:
                break
        else:
            shape = shape.shapes.get_item_by_name(name)
            if not shape:
                break
    return shape
