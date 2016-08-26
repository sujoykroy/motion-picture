from ..commons import *
from shape import Shape
from rectangle_shape import RectangleShape
from oval_shape import OvalShape

class EditBox(object):
    def __init__(self, point, is_percent):
        self.point = point
        self.is_percent = is_percent
        self.init_point = point.copy()
        self.linked_edit_boxes = []

    def reposition(self, rect):
        if self.is_percent:
            self.move_to(rect.left + rect.width*self.point.x, rect.top + rect.height*self.point.y)
        else:
            self.move_to(self.point.x, self.point.y)

    def add_linked_edit_box(self, edit_box):
        self.linked_edit_boxes.append(edit_box)

    def move_offset(self, dx, dy):
        self.point.x = self.init_point.x + dx
        self.point.y = self.init_point.y + dy
        for edit_box in self.linked_edit_boxes:
            edit_box.move_offset(dx, dy)

    def update(self):
        self.init_point.x = self.point.x
        self.init_point.y = self.point.y

    def set_point(self, point):
        self.point.x = point.x
        self.point.y = point.y

class RectEditBox(RectangleShape, EditBox):
    def __init__(self, percent_point, angle=0, is_percent=True, width=10, height=5):
        RectangleShape.__init__(self, Point(width*.5,height*.5), Color(0,0,0,1), 1,
                                      Color(1,1,1,1), width, height, 0)
        EditBox.__init__(self, percent_point, is_percent=is_percent)
        self.set_angle(angle)

class OvalEditBox(OvalShape, EditBox):
    def __init__(self, percent_point, radius=10, fill_color=Color(1,1,1,1), is_percent=True):
        w = h = radius*1.
        OvalShape.__init__(self, Point(w/2,h/2), Color(0,0,0,1), 1, fill_color, w, h, 360)
        EditBox.__init__(self, percent_point, is_percent=is_percent)

class AnchorEditBox(OvalShape, EditBox):
    def __init__(self, shape):
        w = h = 10.
        self.shape = shape
        OvalShape.__init__(self, Point(w/2,h/2), Color(0,0,0,1), 2, Color(1,0,0,1), w, h, 360)
        EditBox.__init__(self, shape.anchor_at.copy(), is_percent=False)

    def move_offset(self, dx, dy):
        EditBox.move_offset(self, dx ,dy)
        self.shape.anchor_at.x = self.point.x
        self.shape.anchor_at.y = self.point.y

class EditLine(Shape):
    def __init__(self, point_1, point_2):
        w = h = 1.0
        Shape.__init__(self, Point(0, 0), Color(0,0,0,1), 1, Color(1,1,1,1), w, h)
        self.point_1 = point_1
        self.point_2 = point_2

    def draw_line(self, ctx):
        ctx.new_path()
        ctx.move_to(self.point_1.x, self.point_1.y)
        ctx.line_to(self.point_2.x, self.point_2.y)

    def set_points(self, point_1, point_2):
        self.point_1.copy_from(point_1)
        self.point_2.copy_from(point_2)


