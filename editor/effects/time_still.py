from MotionPicture.commons import draw_stroke, draw_fill, Point
from MotionPicture import MultiShapeModule
import math
import cairo

class Drawer(object):
    def __init__(self):
        self.params = dict()


    def set_params(self, params):
        self.params = dict(params)

    def set_progress(self, value):
        self.progress = value

    def draw(self, ctx, anchor_at, width, height, parent_shape):
        shape_name = self.params.get("shape_name").decode("utf-8")
        if not shape_name:
            return
        time_line_name = self.params.get("time_line_name").decode("utf-8")
        if not time_line_name:
            return

        orig_shape = parent_shape.get_interior_shape(shape_name)
        shape = orig_shape.copy(deep_copy=True)
        shape.parent_shape = None
        if not shape or not hasattr(shape, "timelines"):
            return

        time_line = shape.timelines.get(time_line_name)
        if not time_line:
            return

        t = 0
        step_count = float(self.params.get("steps",10))
        step_value = 1./step_count
        while t<=self.progress:
            time_line.move_to(time_line.duration*t)
            shape.move_to(anchor_at.x, anchor_at.y)
            t += step_value
            ctx.save()
            shape.draw(ctx, drawing_size=Point(width, height))
            ctx.restore()

