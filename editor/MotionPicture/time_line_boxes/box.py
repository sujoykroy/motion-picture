from ..commons import *

class Box(object):
    IdSeed = 0

    def __init__(self, parent_box=None):
        self.scale_x = 1.
        self.scale_y = 1.
        self.left = 0.
        self.top = 0.
        self.width = 1.
        self.height = 1.
        self.parent_box = parent_box
        self.index = -1
        self.moveable = True
        self.id_num = Box.IdSeed
        Box.IdSeed += 1

    def __eq__(self, other):
        return isinstance(other, Box) and other.id_num == self.id_num

    def copy_into(self, other):
        other.scale_x = self.scale_x
        other.scale_y = self.scale_y
        other.left = self.left
        other.top = self.top
        other.width = self.width
        other.height = self.height

    def set_index(self, index):
        self.index= index

    def move_to(self, point):
        self.left = point.x
        self.top = point.y

    def pre_draw(self, ctx):
        if self.parent_box:
            self.parent_box.pre_draw(ctx)
        ctx.translate(self.left, self.top)
        ctx.scale(self.scale_x, self.scale_y)

    def draw(self, ctx):
        pass

    def abs_transform_point(self, point, only_parent=False):
        if self.parent_box:
            if only_parent:
                point = self.parent_box.rel_transform_point(point)
            else:
                point = self.parent_box.abs_transform_point(point)
        point = self.rel_transform_point(point)
        return point

    def rel_transform_point(self, point):
        point = Point(point.x, point.y)
        point.translate(-self.left, -self.top)
        point.scale(1./self.scale_x, 1./self.scale_y)
        return point

    def rev_rel_transform_point(self, point):
        point = Point(point.x, point.y)
        point.scale(self.scale_x, self.scale_y)
        point.translate(self.left, self.top)
        return point

    def rev_abs_transform_point(self, point, only_parent=False):
        point = self.rev_rel_transform_point(point)
        if self.parent_box:
            if only_parent:
                point = self.parent_box.rev_rel_transform_point(point)
            else:
                point = self.parent_box.rev_abs_transform_point(point)
        return point

    def get_rel_outline(self):
        left_top = self.rev_rel_transform_point(Point(0, 0))
        right_bottom = self.rev_rel_transform_point(Point(self.width, self.height))
        return Rect(left_top.x, left_top.y, right_bottom.x-left_top.x, right_bottom.y-left_top.y)

    def get_abs_outline(self, only_parent=False):
        left_top = self.rev_abs_transform_point(Point(0, 0), only_parent=only_parent)
        right_bottom = self.rev_abs_transform_point(Point(self.width, self.height), only_parent=only_parent)
        return Rect(left_top.x, left_top.y, right_bottom.x-left_top.x, right_bottom.y-left_top.y)

    def is_within(self, point):
        point = self.abs_transform_point(point)
        return point.x>=0 and point.x<=self.width and point.y>=0 and point.y<=self.height
