from ..commons import OrderedDict
from ..commons.draw_utils import *
from box import Box
from sizes import *
from prop_time_line_box import PropTimeLineBox

class ShapeTimeLineBox(Box):
    def __init__(self, shape_time_line, multi_shape_time_line_box):
        Box.__init__(self, multi_shape_time_line_box)
        self.shape_time_line = shape_time_line
        self.prop_time_line_boxes = OrderedDict()
        self.update()

    def update(self):
        for prop_name in self.prop_time_line_boxes.keys:
            if not self.shape_time_line.prop_time_lines.key_exists(prop_name):
                self.prop_time_line_boxes.remove(prop_name)

        height = SHAPE_NAME_HEIGHT
        width = 0
        vert_index = 0
        for prop_time_line in self.shape_time_line.prop_time_lines:
            prop_name = prop_time_line.prop_name
            if not self.prop_time_line_boxes.key_exists(prop_name):
                prop_time_line_box = PropTimeLineBox(prop_time_line, self)
                self.prop_time_line_boxes.insert(vert_index, prop_name, prop_time_line_box)
            else:
                prop_time_line_box = self.prop_time_line_boxes[prop_name]
            prop_time_line_box.set_index(vert_index)
            prop_time_line_box.update()

            height += END_POINT_HEIGHT

            prop_time_line_box.left = 0
            prop_time_line_box.top = height

            height += prop_time_line_box.height
            height += END_POINT_HEIGHT
            if width<prop_time_line_box.width:
                width = prop_time_line_box.width
            vert_index += 1

        self.width = width
        self.height = height + SHAPE_LINE_BOTTOM_PADDING

    def draw(self, ctx):
        draw_text(ctx,
            self.shape_time_line.shape.get_name(), 0, 0, font_name="10",
            text_color = SHAPE_NAME_TEXT_COLOR, padding=5,
            border_color = SHAPE_NAME_BORDER_COLOR, border_width=1,
            back_color = SHAPE_NAME_BACK_COLOR, pre_draw=self.pre_draw)
        for prop_time_line_box in self.prop_time_line_boxes:
            ctx.save()
            prop_time_line_box.draw(ctx)
            ctx.restore()

