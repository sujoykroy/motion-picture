from box import Box
from sizes import *
from ..commons import OrderedDict
from shape_time_line_box import ShapeTimeLineBox

class MultiShapeTimeLineBox(Box):
    def __init__(self, multi_shape_time_line):
        Box.__init__(self)
        self.multi_shape_time_line = multi_shape_time_line
        self.shape_time_line_boxes = OrderedDict()

    def update(self):
        for shape in self.shape_time_line_boxes.keys:
            if not self.multi_shape_time_line.shape_time_lines.key_exists(shape):
                self.shape_time_line_boxes.remove(shape)

        width = height = 0
        vert_index = 0
        for shape_time_line in self.multi_shape_time_line.shape_time_lines:
            shape = shape_time_line.shape
            if not self.shape_time_line_boxes.key_exists(shape):
                shape_time_line_box =  ShapeTimeLineBox(shape_time_line, self)
                self.shape_time_line_boxes.add(shape, shape_time_line_box)
            else:
                shape_time_line_box = self.shape_time_line_boxes[shape]
            shape_time_line_box.set_index(vert_index)
            shape_time_line_box.update()
            outline = shape_time_line_box.get_rel_outline()

            shape_time_line_box.left = SHAPE_LINE_LEFT_PADDING
            shape_time_line_box.top = height

            height += outline.height
            if width<outline.width:
                width = outline.width
            vert_index += 1

        self.width = width + SHAPE_LINE_LEFT_PADDING
        self.height = height

    def draw(self, ctx):
        for shape_time_line_box in self.shape_time_line_boxes:
            ctx.save()
            shape_time_line_box.draw(ctx)
            ctx.restore()

    def update_slices_container_box_left(self, value):
        for shape_line_box in self.shape_time_line_boxes:
            for prop_line_box in shape_line_box.prop_time_line_boxes:
                prop_line_box.slices_container_box.left = value

