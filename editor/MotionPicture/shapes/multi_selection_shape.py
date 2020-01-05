from .multi_shape import MultiShape
from ..commons.draw_utils import draw_rounded_rectangle
from ..commons import Point
from .shape import Shape

MULTI_SELECTION_SHAPE = "MULTI_SELECTION_SHAPE"

class MultiSelectionShape(MultiShape):
    def __init__(self):
        MultiShape.__init__(self, anchor_at=Point(0., 0.))
        self._name = MULTI_SELECTION_SHAPE
        self.parent_list = dict()

    def copy(self, copy_name=False, copy_shapes=True):
        newob = MultiSelectionShape()
        if copy_shapes:
            for shape in self.shapes:
                child_shape = shape.copy(copy_name=True)
                child_shape.parent_shape = newob
                newob.shapes.add(child_shape)
        Shape.copy_into(self, newob, copy_name=copy_name, all_fields=True)
        for shape in self.parent_list:
            new_shape = newob.shapes[shape.get_name()]
            newob.parent_list[new_shape] = self.parent_list[shape]
        return newob

    def add_shape(self, shape, transform=True, resize=True):
        self.parent_list[shape] = shape.parent_shape
        MultiShape.add_shape(self, shape, transform=transform, resize=resize)

    def remove_shape(self, shape, resize=True):
        MultiShape.remove_shape(self, shape, resize)
        shape.parent_shape = self.parent_list[shape]
        del self.parent_list[shape]
        return shape

    def draw(self, ctx):
        for shape in self.shapes:
            outer_rect = shape.get_outline(5)
            ctx.save()
            shape.pre_draw(ctx)
            draw_rounded_rectangle(ctx, outer_rect.left, outer_rect.top,
                    outer_rect.width, outer_rect.height, 0)
            ctx.restore()
            Shape.draw_selection_border(ctx)
