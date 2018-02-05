from ..commons import Point
from ..commons.draw_utils import *
from .sizes import *
from .rect_box import RectBox
from .fixed_size_rect_box import FixedSizeRectBox

class ExpandBox(FixedSizeRectBox):
    def __init__(self, parent_box, move_to_callback):
        self.move_to_callback = move_to_callback
        FixedSizeRectBox.__init__(self, parent_box, 5, HEIGHT_PER_TIME_SLICE, "245672", 1, "dddddd")
        self.yalign = .0

    def move_to(self, point, extra_move_to_callback):
        self.move_to_callback(self, point)
        extra_move_to_callback()

class PointBox(FixedSizeRectBox):
    def __init__(self, parent_box, move_to_callback):
        FixedSizeRectBox.__init__(self, parent_box, 10, END_POINT_HEIGHT, "000000", 1, "ff00ff")
        self.move_to_callback = move_to_callback

    def draw(self, ctx):
        FixedSizeRectBox.draw(self, ctx)
        linked = False
        abs_left_top = self.rev_abs_transform_point(Point(0, 0))
        if self.is_aligned_left:
            prev_time_slice_box = self.parent_box.get_prev_time_slice_box()
            if prev_time_slice_box and prev_time_slice_box.time_slice.linked_to_next:
                linked = True
                x = abs_left_top.x
        else:
            if self.parent_box.time_slice.linked_to_next:
                linked = True
                x = abs_left_top.x-self.width*.5

        if linked:
            draw_rounded_rectangle(ctx, x, abs_left_top.y-self.height*.25, self.width*.5, self.height*.5, 5)
            draw_stroke(ctx, 1, self.border_color)

    def move_to(self, point, extra_move_to_callback):
        RectBox.move_to(self, Point(self.left, point.y))
        self.move_to_callback(self, point)

