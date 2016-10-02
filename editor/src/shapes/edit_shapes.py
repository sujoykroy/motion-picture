from ..commons import *
from shape import Shape
from rectangle_shape import RectangleShape
from oval_shape import OvalShape

MARGIN = 10

class EditBox(object):
    def __init__(self, point, is_percent, offset, angle=0):
        self.point = point
        self.is_percent = is_percent
        self.init_point = point.copy()
        self.linked_edit_boxes = []
        self.abs_point = point.copy()
        self.cpoint = point.copy()
        self.offset = offset
        self.edit_box_angle = angle

    def reposition(self, rect):
        if self.is_percent:
            self.abs_point.x = rect.left + rect.width*self.point.x
            self.abs_point.y = rect.top + rect.height*self.point.y
        else:
            self.abs_point.x = self.point.x
            self.abs_point.y = self.point.y
        self.cpoint = self.abs_reverse_transform_point(self.abs_point)
        if self.offset:
            offset = self.offset.copy()
            offset.rotate_coordinate(-self.abs_angle(0))
            self.cpoint.translate(offset.x, offset.y)

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

    def draw_edit_box(self, ctx, draw_frac=1.):
        ctx.save()
        self._draw_path_around(ctx, self.cpoint, draw_frac)
        self.draw_fill(ctx)
        ctx.restore()
        ctx.save()
        self._draw_path_around(ctx, self.cpoint, draw_frac)
        self.draw_border(ctx)
        ctx.restore()

class RectEditBox(RectangleShape, EditBox):
    def __init__(self, percent_point, angle=0, is_percent=True, width=10, height=5, offset=None):
        RectangleShape.__init__(self, Point(width*.5,height*.5), Color(0,0,0,1), 1,
                                      Color(1,1,1,1), width, height, 0)
        EditBox.__init__(self, percent_point, is_percent=is_percent, offset=offset, angle=angle)

    def _draw_path_around(self, ctx, cpoint, draw_frac):
        ctx.translate(cpoint.x, cpoint.y)
        ctx.rotate(self.abs_angle(self.edit_box_angle)*RAD_PER_DEG)
        draw_rounded_rectangle(ctx,
            -self.width*.5, -self.height*.5, self.width, self.height, 1)

    def is_within(self, point):
        if not self.cpoint: return False
        point = point.copy()
        point.translate(-self.cpoint.x, -self.cpoint.y)
        point.rotate_coordinate(self.abs_angle(self.edit_box_angle))
        return self.width*.5>=point.x and point.x>=-self.width*.5 and \
               self.height*.5>=point.y and point.y>=-self.height*.5

class OvalEditBox(OvalShape, EditBox):
    def __init__(self, percent_point, radius=10, fill_color=Color(1,1,1,1),
                       is_percent=True, offset=None):
        w = h = radius*1.
        self.radius = radius
        OvalShape.__init__(self, Point(w/2,h/2), Color(0,0,0,1), 1, fill_color, w, h, 360)
        EditBox.__init__(self, percent_point, is_percent=is_percent, offset=offset)

    def _draw_path_around(self, ctx, cpoint, draw_frac):
        ctx.new_path()
        ctx.move_to(cpoint.x+self.radius*draw_frac, cpoint.y)
        ctx.arc(cpoint.x, cpoint.y, self.radius*draw_frac, 0, 360*RAD_PER_DEG)
        ctx.close_path()

    def is_within(self, point):
        if not self.cpoint: return False
        return self.cpoint and self.cpoint.distance(point)<=self.radius

class AnchorEditBox(OvalEditBox):
    def __init__(self, shape):
        w = h = 10.
        OvalEditBox.__init__(self, shape.anchor_at.copy(),
                    radius=10, fill_color=Color(1,0,0,1), is_percent=False)
        self.shape = shape

    def move_offset(self, dx, dy):
        OvalEditBox.move_offset(self, dx ,dy)
        self.shape.anchor_at.x = self.point.x
        self.shape.anchor_at.y = self.point.y

class OutlineEditBox(RectEditBox):
    def __init__(self, shape):
        RectEditBox.__init__(self, Point(0,0))
        self.shape = shape

    def draw(self, ctx):
        points = []
        points.append(Point(0, 0))
        points.append(Point(self.shape.width, 0))
        points.append(Point(self.shape.width, self.shape.height))
        points.append(Point(0, self.shape.height))
        angle = self.shape.abs_angle(0)
        for i in range(len(points)):
            points[i] = self.shape.abs_reverse_transform_point(points[i])
            if i == 0:
                offset = Point(-MARGIN, -MARGIN)
            elif i == 1:
                offset = Point(MARGIN, -MARGIN)
            elif i == 2:
                offset = Point(MARGIN, MARGIN)
            elif i == 3:
                offset = Point(-MARGIN, MARGIN)
            offset.rotate_coordinate(-angle)
            points[i].translate(offset.x, offset.y)

        cpoint = self.shape.abs_reverse_transform_point(
                    Point(self.shape.width*.5, self.shape.height*.5))
        ctx.save()
        ctx.new_path()
        for i in range(len(points)):
            if i == 0:
                ctx.move_to(points[i].x, points[i].y)
            else:
                ctx.line_to(points[i].x, points[i].y)
        ctx.close_path()
        ctx.restore()
        draw_selection_border(ctx)

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


