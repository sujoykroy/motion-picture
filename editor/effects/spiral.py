from MotionPicture.commons import draw_stroke, Point, color_from_text, Color
from MotionPicture import TextShape
import numpy
import math

class Drawer(object):
    def __init__(self):
        self.params = dict()
        self.params_info = dict(
            line_color=dict(type="color", default=Color(0,0,0,1)),
            line_width=dict(type="number", default=1, lower=0),
            a=dict(type="number", default=0),
            b=dict(type="number", default=5),
            c=dict(type="number", default=1),
            loop=dict(type="number", default=7),
            steps=dict(type="int", default=50, lower=1),
        )
        self.use_custom_surface = False

    def set_params(self, params):
        self.params.update(params)
        self.params["line_color"] = color_from_text(self.params["line_color"])

    def set_progress(self, value):
        self.progress = value

    def get_baked_point(self, frac):
        loop =  self.params.get("loop")
        a = self.params.get("a")
        b = self.params.get("b")
        c = self.params.get("c")
        angles = numpy.array([frac, frac+.0001])*loop*math.pi*2
        rs = a +b*(angles**(1./c))
        xs = rs*numpy.cos(angles)
        ys = rs*numpy.sin(angles)
        sp = Point(xs[0], ys[0])
        ep = Point(xs[1], ys[1])
        dp = ep.diff(sp)
        return sp, dp.get_angle()

    def draw(self, ctx, anchor_at, width, height, parent_shape):
        loop =  self.params.get("loop")
        steps = self.params.get("steps")

        a = self.params.get("a")
        b = self.params.get("b")
        c = self.params.get("c")
        angles = numpy.linspace(0, loop*math.pi*2, endpoint=True, num=steps*loop)
        rs = a +b*(angles**(1./c))
        xs = rs*numpy.cos(angles)
        ys = rs*numpy.sin(angles)

        ctx.translate(anchor_at.x, anchor_at.y)
        i = 0
        while i<len(angles):
            x = xs[i]
            y = ys[i]
            if not numpy.isinf(x) and not  numpy.isinf(y) and \
                x>=-anchor_at.x and x<=width-anchor_at.x and y>=-anchor_at.y and y<=height-anchor_at.y:
                if i == 0:
                    ctx.move_to(x, y)
                else:
                    ctx.line_to(x, y)
            i += 1
        draw_stroke(ctx, self.params.get("line_width"), self.params.get("line_color"))
