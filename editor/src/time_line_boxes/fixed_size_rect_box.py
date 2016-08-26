from ..commons import Point
from ..commons.draw_utils import *
from rect_box import RectBox

class FixedSizeRectBox(RectBox):
    def __init__(self, parent_box, width, height, border_color, border_width, fill_color):
        RectBox.__init__(self, parent_box, width, height, border_color, border_width, fill_color)
        self.is_aligned_left = True
        self.is_height_fixed = True
        self.yalign = .5

    def set_right(self, right):
        self.left = right
        self.is_aligned_left = False

    def set_vert_center(self, value):
        self.top = value

    def is_within(self, point):
        abs_left_top = self.rev_abs_transform_point(Point(0, 0))
        if not self.is_height_fixed:
            abs_left_bottom = self.rev_abs_transform_point(Point(0, self.height))
            height = abs_left_bottom.y - abs_left_top.y
        else:
            height = self.height
        if self.is_aligned_left:
           return (point.x>=abs_left_top.x and point.x<=abs_left_top.x+self.width and \
                   point.y>=abs_left_top.y-height*self.yalign and \
                   point.y<=abs_left_top.y+height*(1-self.yalign))
        else:
           return (point.x>=abs_left_top.x-self.width and point.x<=abs_left_top.x and \
                   point.y>=abs_left_top.y-height*self.yalign and \
                   point.y<=abs_left_top.y+height*(1-self.yalign))

    def draw_path(self, ctx):
        abs_left_top = self.rev_abs_transform_point(Point(0, 0))
        if not self.is_height_fixed:
            abs_left_bottom = self.rev_abs_transform_point(Point(0, self.height))
            height = abs_left_bottom.y - abs_left_top.y
        else:
            height = self.height
        if self.is_aligned_left:
            draw_rounded_rectangle(ctx, abs_left_top.x, abs_left_top.y-height*self.yalign,
                                         self.width, height, 5)
        else:
            draw_rounded_rectangle(ctx, abs_left_top.x-self.width, abs_left_top.y-height*self.yalign,
                                         self.width, height, 5)

    def draw(self, ctx):
        if self.fill_color:
            self.draw_path(ctx)
            draw_fill(ctx, self.fill_color)

        if self.border_color:
            self.draw_path(ctx)
            draw_stroke(ctx, self.border_width, self.border_color)

