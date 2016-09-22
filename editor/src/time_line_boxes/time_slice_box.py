from ..commons.draw_utils import *
from sizes import *
from box import Box
from edit_boxes import *
from ..time_lines.time_change_types import *

class TimeSliceBox(Box):
    def __init__(self, time_slice, prop_time_line_box):
        Box.__init__(self, prop_time_line_box.slices_container_box)
        self.prop_time_line_box = prop_time_line_box
        self.time_slice = time_slice
        self.edit_boxes = []

        self.left_point_box = PointBox(self, self.left_point_move_to_callback)
        self.right_point_box = PointBox(self, self.right_point_move_to_callback)
        self.right_expand_box = ExpandBox(self, self.right_expand_move_to_callback)
        self.right_expand_box.is_height_fixed = False
        self.right_expand_box.corner_radius = 0.

        self.edit_boxes.append(self.right_expand_box)
        self.edit_boxes.append(self.left_point_box)
        self.edit_boxes.append(self.right_point_box)

        self.highlighted = False

    def get_next_time_slice_box(self):
        return self.prop_time_line_box.get_time_slice_box_at_index(self.index+1)

    def get_prev_time_slice_box(self):
        return self.prop_time_line_box.get_time_slice_box_at_index(self.index-1)

    def update_prev_linked_box(self):
        prev_time_slice_box = self.get_prev_time_slice_box()
        if prev_time_slice_box and prev_time_slice_box.time_slice.linked_to_next:
            prev_time_slice_box.time_slice.end_value = self.time_slice.start_value
            prev_time_slice_box.update()

    def update_next_linked_box(self):
        if self.time_slice.linked_to_next:
            next_time_slice_box = self.get_next_time_slice_box()
            if next_time_slice_box:
                next_time_slice_box.time_slice.start_value = self.time_slice.end_value
                next_time_slice_box.update()

    def left_point_move_to_callback(self, point_box, point):
        y = point.y
        value = y/self.prop_time_line_box.y_per_value
        value = self.prop_time_line_box.max_value-value
        self.time_slice.start_value = value
        self.update_prev_linked_box()

    def right_point_move_to_callback(self, point_box, point):
        y = point.y
        value = y/self.prop_time_line_box.y_per_value
        value = self.prop_time_line_box.max_value-value
        self.time_slice.end_value = value
        self.update_next_linked_box()

    def right_expand_move_to_callback(self, expand_box, point):
        duration = point.x/PIXEL_PER_SECOND
        if duration>0:
            self.time_slice.duration = duration
        self.prop_time_line_box.update()

    def update(self):
        self.width = self.time_slice.duration*PIXEL_PER_SECOND
        self.height = HEIGHT_PER_TIME_SLICE
        self.right_expand_box.set_right(self.width)

        self.left_point_box.set_left(0)
        self.left_point_box.set_vert_center(
         (self.prop_time_line_box.max_value -
                self.time_slice.start_value)*self.prop_time_line_box.y_per_value)

        self.right_point_box.set_right(self.width)
        self.right_point_box.set_vert_center(
            (self.prop_time_line_box.max_value -
                self.time_slice.end_value)*self.prop_time_line_box.y_per_value)

    def draw(self, ctx):
        ctx.save()
        self.pre_draw(ctx)
        draw_rounded_rectangle(ctx, 0, 0, self.width, self.height, 0)
        if self.highlighted:
            draw_fill(ctx, "D6E424")
        else:
            draw_fill(ctx, "eda4b5")
        draw_rounded_rectangle(ctx, 0, 0, self.width, self.height, 0)
        ctx.restore()
        draw_stroke(ctx, 1, "000000")

        for edit_box in self.edit_boxes:
            ctx.save()
            edit_box.draw(ctx)
            ctx.restore()

        change_type = self.time_slice.change_type
        time_slice = self.time_slice

        ctx.save()
        self.pre_draw(ctx)
        ctx.scale(PIXEL_PER_SECOND, self.prop_time_line_box.y_per_value)
        ctx.translate(0, self.prop_time_line_box.max_value)
        ctx.scale(1, -1)

        if isinstance(change_type, PeriodicChangeType):
            total_steps = int(self.time_slice.duration*self.parent_box.scale_x*PIXEL_PER_SECOND)
            for i in range(total_steps):
                x = i*self.time_slice.duration/total_steps
                y = self.time_slice.value_at(x)
                if i == 0:
                    ctx.move_to(x, y)
                else:
                    ctx.line_to(x, y)
        elif isinstance(self.time_slice.change_type, TimeChangeType):
            draw_straight_line(ctx, 0, self.time_slice.start_value,
                        self.time_slice.duration, self.time_slice.end_value)

        ctx.restore()
        draw_stroke(ctx, 1, "000000")

        if False and self.highlighted:
            ctx.save()
            self.pre_draw(ctx)
            draw_rounded_rectangle(ctx, 0, 0, self.width, self.height, 0)
            ctx.restore()
            draw_stroke(ctx, 5, "ff000044")


