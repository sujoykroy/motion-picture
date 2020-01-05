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
        shape.parent_shape = parent_shape
        if not shape or not hasattr(shape, "timelines"):
            return

        time_line = shape.timelines.get(time_line_name)
        if not time_line:
            return
        time_line.move_to(0)
        #shape = shape.copy(deep_copy=True)
        #shape.parent_shape = None
        #time_line = shape.timelines.get(time_line_name)

        t = 0
        step_count = float(self.params.get("steps",10))
        step_value = 1./step_count
        while t<=self.progress+step_value:
            time_line.move_to(time_line.duration*t)
            t += step_value
            ctx.save()
            shape.set_scale_x(width/shape.width)
            shape.set_scale_y(height/shape.height)

            parent_shape = shape.parent_shape
            shape.parent_shape = None
            shape.move_to(anchor_at.x, anchor_at.y)
            shape.draw(ctx, drawing_size=Point(width, height))
            shape.parent_shape = parent_shape
            ctx.restore()
