from .box import Box
from ..commons.colors import Color
from ..commons.draw_utils import *

class RectBox(Box):
    def __init__(self, parent_box, width, height, border_color, border_width, fill_color):
        Box.__init__(self, parent_box)
        self.width = width
        self.height = height
        self.border_color = Color.parse(border_color)
        self.fill_color = Color.parse(fill_color)
        self.border_width = border_width

    def draw_path(self, ctx):
        draw_rounded_rectangle(ctx, 0, 0, self.width, self.height, 5)

    def set_left(self, left):
        self.left = left

    def set_right(self, right):
        self.left = right-self.width

    def set_vert_center(self, value):
        self.top = value - self.height*.5

    def draw(self, ctx):
        if self.fill_color:
            ctx.save()
            self.pre_draw(ctx)
            self.draw_path(ctx)
            ctx.restore()
            draw_fill(ctx, self.fill_color)

        if self.border_color:
            ctx.save()
            self.pre_draw(ctx)
            self.draw_path(ctx)
            ctx.restore()
            draw_stroke(ctx, self.border_width, self.border_color)

    def set_scale(self, scale_x, scale_y):
        self.scale_x = scale_x
        self.scale_y = scale_y
