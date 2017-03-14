from ..commons import OrderedDict
from ..commons.draw_utils import *
from box import Box
from sizes import *
from time_slice_box import TimeSliceBox
from .. import settings

class PropTimeLineBox(Box):
    TOTAL_LABEL_WIDTH = PROP_NAME_LABEL_WIDTH + PROP_VALUE_LABEL_WIDTH + 6*PROP_NAME_LABEL_RIGHT_PADDING

    def __init__(self, prop_time_line, shape_time_line_box):
        Box.__init__(self, shape_time_line_box)
        self.prop_time_line = prop_time_line
        self.time_slice_boxes = OrderedDict()
        self.y_per_value = 1
        self.min_value = -1
        self.max_value = 1
        self.slices_container_box = Box(self)
        self.slices_container_box.left = self.TOTAL_LABEL_WIDTH
        self.vertical_zoom = 1.
        self.update()

    def get_time_slice_box_at_index(self, index):
        return self.time_slice_boxes.get_item_at_index(index)

    def set_time_multiplier(self, scale):
        self.slices_container_box.scale_x = scale

    def set_vertical_multiplier(self, scale):
        self.slices_container_box.scale_y *= scale

    def update(self):
        min_value, max_value = self.prop_time_line.get_min_max_value()
        if max_value == min_value:
            max_value = min_value + 1
        diff = float(max_value-min_value)
        self.max_value = max_value + diff*.05
        self.min_value = min_value - diff*.05
        self.y_per_value = HEIGHT_PER_TIME_SLICE/(self.max_value-self.min_value)

        for time_slice in self.time_slice_boxes.keys:
            if not self.prop_time_line.time_slices.key_exists(time_slice):
                self.time_slice_boxes.remove(time_slice)

        scaled_width = 0
        width = 0
        height = 0
        horiz_index = 0
        for time_slice in self.prop_time_line.time_slices:
            if not self.time_slice_boxes.key_exists(time_slice):
                time_slice_box = TimeSliceBox(time_slice, self)
                self.time_slice_boxes.insert(horiz_index, time_slice, time_slice_box)
            else:
                time_slice_box = self.time_slice_boxes[time_slice]
            time_slice_box.set_index(horiz_index)
            time_slice_box.update()
            time_slice_box.left = width
            time_slice_box.top = 0

            outline = time_slice_box.get_rel_outline()
            width += outline.width
            if height<outline.height:
                height = outline.height#*self.slices_container_box.scale_y
            horiz_index += 1

        self.width = width*self.slices_container_box.scale_x + self.slices_container_box.left
        self.height = height*self.slices_container_box.scale_y + PROP_TIME_LINE_VERTICAL_PADDING

    def draw(self, ctx, visible_time_span):
        ctx.save()
        self.pre_draw(ctx)
        ctx.rectangle(0, 0, 2000, self.height-PROP_TIME_LINE_VERTICAL_PADDING)
        ctx.restore()
        draw_stroke(ctx, 1, "aaaaaa")

        for time_slice in self.prop_time_line.time_slices:
            time_slice_box = self.time_slice_boxes[time_slice]
            ctx.save()
            time_slice_box.draw(ctx, visible_time_span)
            ctx.restore()

        ctx.save()
        self.pre_draw(ctx)
        ctx.rectangle(-SHAPE_LINE_LEFT_PADDING-2, -5,
                    PropTimeLineBox.TOTAL_LABEL_WIDTH+SHAPE_LINE_LEFT_PADDING, self.height+5)
        ctx.restore()
        draw_fill(ctx, PROP_LEFT_BACK_COLOR)

        draw_text(ctx,
            self.prop_time_line.prop_name, 0, 0, font_name=settings.TIME_LINE_FONT,
            width=PROP_NAME_LABEL_WIDTH,
            text_color = PROP_NAME_TEXT_COLOR, padding=PROP_NAME_LABEL_RIGHT_PADDING,
            border_color = PROP_NAME_BORDER_COLOR, border_width=2,
            back_color = PROP_NAME_BACK_COLOR, pre_draw=self.pre_draw)

        value_x_pos = PROP_NAME_LABEL_WIDTH + 3*PROP_NAME_LABEL_RIGHT_PADDING + PROP_VALUE_LABEL_WIDTH

        draw_text(ctx, "{0:.2f}".format(self.max_value), font_name="7",
                  x=value_x_pos, align="right bottom-center",
                  width=PROP_VALUE_LABEL_WIDTH, fit_width=True,
                  y=0, text_color="000000", pre_draw=self.pre_draw)

        draw_text(ctx, "{0:02.2f}".format(self.min_value), font_name="7",
                  x=value_x_pos, align="right bottom",
                  width=PROP_VALUE_LABEL_WIDTH, fit_width=True,
                  y=self.height, text_color="000000", pre_draw=self.pre_draw)

        ctx.save()
        self.pre_draw(ctx)
        draw_straight_line(ctx, value_x_pos, 0, value_x_pos+2*PROP_NAME_LABEL_RIGHT_PADDING, 0)
        draw_stroke(ctx, 1)
        draw_straight_line(ctx, value_x_pos, self.height-END_POINT_HEIGHT*.5,
                                value_x_pos+2*PROP_NAME_LABEL_RIGHT_PADDING,
                                self.height-END_POINT_HEIGHT*.5)
        draw_stroke(ctx, 1)
        ctx.restore()


