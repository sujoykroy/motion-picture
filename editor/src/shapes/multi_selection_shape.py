from multi_shape import MultiShape

MULTI_SELECTION_SHAPE = "MULTI_SELECTION_SHAPE"

class MultiSelectionShape(MultiShape):
    def __init__(self):
        MultiShape.__init__(self)
        self._name = MULTI_SELECTION_SHAPE
        self.parent_list = dict()

    def add_shape(self, shape):
        self.parent_list[shape] = shape.parent_shape
        MultiShape.add_shape(self, shape)

    def remove_shape(self, shape):
        MultiShape.remove_shape(self, shape)
        shape.parent_shape = self.parent_list[shape]
        del self.parent_list[shape]
        return shape

    def draw(self, ctx):
        for shape in self.shapes:
            outer_rect = shape.get_outline(5)
            ctx.save()
            shape.pre_draw(ctx)
            Shape.rounded_rectangle(ctx, outer_rect.left, outer_rect.top,
                    outer_rect.width, outer_rect.height, 0)
            ctx.restore()
            Shape.draw_selection_border(ctx)
