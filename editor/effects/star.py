from MotionPicture.commons import draw_stroke, draw_fill, Point, Polygon, Color
from MotionPicture import CurveShape, PolygonShape
import math
import cairo

class Drawer(object):
    def __init__(self):
        self.params = dict()

    def set_params(self, params):
        self.params = dict(params)

    def set_progress(self, value):
        self.progress = value

    def get_seed_shape(self, width=100., height=100.):
        ofx = .125
        ofy = .5
        points = [
            [-ofx, 0+ofy], [.5, -.5] , [1+ofx, 0+ofy],
            [1+ofx*1.5, ofy*1.5], [1, 1], 
            [0, 1], [-ofx*1.5, ofy*1.5]
        ]
        polygon = Polygon(points=points, closed=True)
        seed_shape = PolygonShape(width=width, height=height, anchor_at=Point(width*.5, height))
        seed_shape.add_polygon(polygon)
        return seed_shape

    def draw(self, ctx, anchor_at, width, height, parent_shape):
        steps = 200

        seed_shape = self.get_seed_shape(width=10)
        seed_shape.set_same_xy_scale(True)
        seed_shape.move_to(50, 100)

        start_color = Color(0., 0., 0., 1.)
        end_color = Color(1., 1., 1., 1.)
        color = end_color.copy()

        for ai in xrange(angle_steps):
            ai = 360*(ai*1./angle_steps)
            for i in xrange(steps):
                frac = 1-(i+1)*1./steps                
                seed_shape.set_scale_x(frac)
                seed_shape.angle = ai
                color.set_inbetween(end_color, start_color, frac)

                ctx.save()
                ctx.scale(width*.01, height*.01)

                seed_shape.pre_draw(ctx)
                seed_shape.draw_path(ctx, for_fill=True)

                ctx.restore()
                draw_fill(ctx, color)
