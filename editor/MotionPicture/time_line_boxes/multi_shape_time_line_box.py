from .box import Box
from .sizes import *
from ..commons import OrderedDict
from .shape_time_line_box import ShapeTimeLineBox

class MultiShapeTimeLineBox(Box):
    def __init__(self, multi_shape_time_line):
        Box.__init__(self)
        self.time_line_width = 0
        self.multi_shape_time_line = multi_shape_time_line
        self.shape_time_line_boxes = OrderedDict()

    def get_multi_shape_time_line(self):
        return self.multi_shape_time_line

    def shape_exists(self, shape):
        return self.shape_time_line_boxes.key_exists(shape)

    def get_shape_count(self):
        return len(self.shape_time_line_boxes)

    def print_index_data(self):
        shape_indices = []
        for shape_time_line_box in self.shape_time_line_boxes:
            prop_indices = []
            for prop_time_line_box in shape_time_line_box.prop_time_line_boxes:
                slice_indices = []
                for time_slice in prop_time_line_box.time_slice_boxes.keys:
                    time_slice_box = prop_time_line_box.time_slice_boxes[time_slice]
                    slice_indices.append("ID:{0}, Index: {1}".format(
                        time_slice.id_num, time_slice_box.index))
                prop_indices.append("Prop:{0}\nSlices:{1}".format(
                        prop_time_line_box.prop_time_line.prop_name, ", ".join(slice_indices)))
            shape_indices.append("Shape:{1}\nProps:{1}".format(
                shape_time_line_box.shape_time_line.shape.get_name(), "\n".join(prop_indices)))
        print("\nINDEX Data \n".join(shape_indices))

    def update(self):
        for shape in self.shape_time_line_boxes.keys:
            if not self.multi_shape_time_line.shape_time_lines.key_exists(shape):
                self.shape_time_line_boxes.remove(shape)

        width = height = 0
        vert_index = 0
        self.time_line_width = 0
        for shape_time_line in self.multi_shape_time_line.shape_time_lines:
            shape = shape_time_line.shape
            if not self.shape_time_line_boxes.key_exists(shape):
                shape_time_line_box =  ShapeTimeLineBox(shape_time_line, self)
                self.shape_time_line_boxes.insert(vert_index, shape, shape_time_line_box)
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
            if self.time_line_width<shape_time_line_box.time_line_width:
                self.time_line_width = shape_time_line_box.time_line_width

        self.width = width + SHAPE_LINE_LEFT_PADDING
        self.height = height

    def draw(self, ctx, visible_time_span, shape=None):
        for shape_time_line_box in self.shape_time_line_boxes:
            selected = shape_time_line_box.shape_time_line.shape == shape
            ctx.save()
            shape_time_line_box.draw(ctx, selected=selected, visible_time_span=visible_time_span)
            ctx.restore()

    def update_slices_container_box_left(self, value):
        for shape_line_box in self.shape_time_line_boxes:
            for prop_line_box in shape_line_box.prop_time_line_boxes:
                prop_line_box.slices_container_box.left = value
