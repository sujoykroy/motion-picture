from ..commons.draw_utils import *
from ..commons import copy_value
from .sizes import *
from .box import Box
from .edit_boxes import *
from ..time_lines.time_change_types import *
from ..shapes import AudioShape

class TimeSliceBox(Box):
    def __init__(self, time_slice, prop_time_line_box):
        Box.__init__(self, prop_time_line_box.slices_container_box)
        self.prop_time_line_box = prop_time_line_box
        self.time_slice = time_slice
        self.edit_boxes = []

        self.right_expand_box = ExpandBox(self, self.right_expand_move_to_callback)
        self.right_expand_box.is_height_fixed = False
        self.right_expand_box.corner_radius = 0.
        self.edit_boxes.append(self.right_expand_box)

        if not time_slice.has_multiple_prop():
            self.left_point_box = PointBox(self, self.left_point_move_to_callback)
            self.right_point_box = PointBox(self, self.right_point_move_to_callback)

            self.edit_boxes.append(self.left_point_box)
            self.edit_boxes.append(self.right_point_box)
        else:
            self.left_point_box = None
            self.right_point_box = None
        self.highlighted = False


    def is_moveable_edit_box(self, edit_box):
        if edit_box == self.right_expand_box and self.time_slice.end_marker:
            return False
        return True

    def get_multi_shape_time_line(self):
        return self.prop_time_line_box.get_multi_shape_time_line()

    def get_prop_time_line(self):
        return self.prop_time_line_box.prop_time_line

    def get_next_time_slice_box(self):
        return self.prop_time_line_box.get_time_slice_box_at_index(self.index+1)

    def get_prev_time_slice_box(self):
        return self.prop_time_line_box.get_time_slice_box_at_index(self.index-1)

    def update_prev_linked_box(self):
        prev_time_slice_box = self.get_prev_time_slice_box()
        if prev_time_slice_box and prev_time_slice_box.time_slice.linked_to_next:
            prev_time_slice_box.time_slice.end_value = copy_value(self.time_slice.start_value)
            prev_time_slice_box.update()

    def update_next_linked_box(self):
        if self.time_slice.linked_to_next:
            next_time_slice_box = self.get_next_time_slice_box()
            if next_time_slice_box:
                next_time_slice_box.time_slice.start_value = copy_value(self.time_slice.end_value)
                next_time_slice_box.update()

    def left_point_move_to_callback(self, point_box, point):
        y = point.y
        value = y/self.prop_time_line_box.y_per_value
        value = self.prop_time_line_box.max_value-value
        self.time_slice.start_value = copy_value(value)
        self.update_prev_linked_box()

    def right_point_move_to_callback(self, point_box, point):
        y = point.y
        value = y/self.prop_time_line_box.y_per_value
        value = self.prop_time_line_box.max_value-value
        self.time_slice.end_value = copy_value(value)
        self.update_next_linked_box()

    def right_expand_move_to_callback(self, expand_box, point):
        duration = point.x/PIXEL_PER_SECOND
        if duration>0:
            self.change_duration(duration)
        self.prop_time_line_box.update()

    def update(self):
        self.width = self.time_slice.duration*PIXEL_PER_SECOND
        self.height = HEIGHT_PER_TIME_SLICE
        self.right_expand_box.set_right(self.width)

        if self.left_point_box:
            self.left_point_box.set_left(0)
            self.left_point_box.set_vert_center(
             (self.prop_time_line_box.max_value -
                    self.time_slice.start_value)*self.prop_time_line_box.y_per_value)

        if self.right_point_box:
            self.right_point_box.set_right(self.width)
            self.right_point_box.set_vert_center(
                (self.prop_time_line_box.max_value -
                    self.time_slice.end_value)*self.prop_time_line_box.y_per_value)

    def draw(self, ctx, visible_time_span):
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

        #draw audio_shape wave
        prop_time_line = self.prop_time_line_box.prop_time_line
        shape = prop_time_line.shape
        prop_name = prop_time_line.prop_name
        if shape.can_draw_time_slice_for(prop_name):
            shape.draw_for_time_slice(
                    ctx, prop_name, self.time_slice.prop_data, visible_time_span,
                    self.time_slice, self, PIXEL_PER_SECOND)

        ctx.save()
        self.pre_draw(ctx)
        ctx.scale(PIXEL_PER_SECOND, self.prop_time_line_box.y_per_value)
        ctx.translate(0, self.prop_time_line_box.max_value)
        ctx.scale(1, -1)
        time_end = min(time_slice.duration, visible_time_span.end)

        t = visible_time_span.start
        t_step = 1./(visible_time_span.scale*PIXEL_PER_SECOND)
        draw_started = False
        paths = []
        if isinstance(change_type, PeriodicChangeType) or \
           isinstance(change_type, LoopChangeType):
            while t<time_end:
                y = self.time_slice.value_at(t)
                if self.time_slice.has_multiple_prop():
                    for i in range(len(y)):
                        if len(paths)<=i:
                            paths.append([])
                        paths[i].append((t, y[i]))
                else:
                    if not draw_started:
                        ctx.move_to(t, y)
                        draw_started = True
                    else:
                        ctx.line_to(t, y)
                t += t_step
        elif isinstance(self.time_slice.change_type, TimeChangeType):
            if self.time_slice.has_multiple_prop():
                for i in range(len(self.time_slice.start_value)):
                    if len(paths)<=i:
                        paths.append([])
                    paths[i].append((0, self.time_slice.start_value[i]))
                    paths[i].append((self.time_slice.duration, self.time_slice.end_value[i]))
            else:
                draw_straight_line(ctx, 0, self.time_slice.start_value,
                            self.time_slice.duration, self.time_slice.end_value)


        if paths:
            for p in range(len(paths)):
                path = paths[p]
                ctx.new_path()
                for i in range(len(path)):
                    if i == 0:
                        ctx.move_to(path[i][0], path[i][1])
                    else:
                        ctx.line_to(path[i][0], path[i][1])
                paths[p] = ctx.copy_path()
            ctx.new_path()
            for path in paths:
                ctx.append_path(path)
        ctx.restore()
        draw_stroke(ctx, 1, "000000")

        if False and self.highlighted:
            ctx.save()
            self.pre_draw(ctx)
            draw_rounded_rectangle(ctx, 0, 0, self.width, self.height, 0)
            ctx.restore()
            draw_stroke(ctx, 5, "ff000044")

    def change_duration(self, duration):
        prop_time_line = self.get_prop_time_line()
        return prop_time_line.change_time_slice_duration(self.time_slice, duration)

    def sync_with_time_marker(self, time_marker):
        multi_shape_time_line = self.get_multi_shape_time_line()
        prop_time_line = self.get_prop_time_line()
        multi_shape_time_line.sync_time_slices_with_time_marker(
                    time_marker, prop_time_line=prop_time_line)
