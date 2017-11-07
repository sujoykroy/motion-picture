from MotionPicture.commons import draw_stroke, draw_fill, Point, Polygon, Color, draw_oval
from MotionPicture.commons import color_from_text
from MotionPicture import CurveShape, PolygonShape
import math
import cairo

class Drawer(object):
    def __init__(self):
        self.params = dict()
        self.params_info = dict(
            size_steps=dict(type="int", default=10, lower=1, upper=1000000),
            angle_steps=dict(type="int", default=4, lower=1, upper=1000000),
            sw=dict(type="number", default=50, lower=.01, upper=100, step_increment=1),
            sh=dict(type="number", default=50, lower=.01, upper=100, step_increment=1),
            d1=dict(type="number", default=12, lower=0, upper=100, step_increment=1),
            d2=dict(type="number", default=50, lower=0, upper=100, step_increment=1),
            d3=dict(type="number", default=50, lower=0, upper=100, step_increment=1),
            theta=dict(type="number", default=20, lower=0, upper=360, step_increment=1),
            start_color=dict(type="color", default="FFFFFF00"),
            end_color=dict(type="color", default="FFFFFFFF"),
            fill_star=dict(type="int", default=1, lower=0, upper=1),
        )

        self.image_surface = None
        self.image_name = None

    def set_params(self, params):
        if params != self.params:
            self.params = dict(params)
        self.params["start_color"] = color_from_text(self.params["start_color"])
        self.params["end_color"] = color_from_text(self.params["end_color"])
        self.image_name = None

    def set_progress(self, value):
        self.progress = value
        self.image_name = None

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
        image_name = "{0}x{1}".format(width, height)
        if self.image_name != image_name or not self.image_surface:
            image_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
            image_ctx = cairo.Context(image_surface)
            self.draw_image(image_ctx, anchor_at, width, height, parent_shape)
            self.image_surface = image_surface
            self.image_name = image_name

        ctx.set_source_surface(self.image_surface)
        ctx.rectangle(0,0,width,height)
        ctx.paint()

    def draw_image(self, ctx, anchor_at, width, height, parent_shape):
        seed_shape = self.get_seed_shape(width=10)
        seed_shape.set_same_xy_scale(True)
        seed_shape.move_to(50, 100)

        start_color = Color.parse(self.params.get("start_color", parent_shape.get_fill_color()))
        end_color = Color.parse(self.params.get("end_color", Color(1., 1., 1., 1.)))

        color = end_color.copy()

        sw = self.params.get("sw", 50.)
        sh = self.params.get("sh", 50.)

        sw_squeeze = 0.
        sh_squeeze = 0.

        frac_offset_y = 0.0
        frac_offset_x = 0.0

        size_steps = self.params.get("size_steps", 10)
        angle_steps = self.params.get("angle_steps", 8)

        d1 = self.params.get("d1", 12.5)*.01
        d2 = self.params.get("d2", 50)*.01
        d3 = self.params.get("d3", 50)*.01
        theta =self.params.get("theta", 20)*(math.pi/180.)

        angle_incre = math.pi/angle_steps
        p1 = Point(-d1*math.sin(angle_incre), -d1*math.cos(angle_incre))

        p2 = p1.copy()
        p2.translate(d2*math.cos(angle_incre), -d2*math.sin(angle_incre))

        p4 = Point(0, -1)
        p3 = p4.copy()
        p3.translate(-d3*math.sin(theta), d3*math.cos(theta))

        should_fill = bool(self.params.get("fill_star", True))
        border_color = parent_shape.get_border_color()

        for i in xrange(size_steps):
            frac = 1-i*1./size_steps
            frac_x = frac_offset_x + (1-frac_offset_x)*(frac**5)
            frac_y = frac_offset_y + (1-frac_offset_y)*(frac**5)

            color.set_inbetween(start_color, end_color, i*1./size_steps)

            ctx.save()
            ctx.scale(width*.01, height*.01)
            ctx.translate(50, 50)
            ctx.scale(height/width, 1)
            ctx.scale(frac_x, frac_y)

            for ai in xrange(angle_steps):
                ai = 2*math.pi*(ai*1./angle_steps)

                ctx.save()
                ctx.rotate(ai)
                ctx.scale(sw, sh)

                for p in []:
                    ctx.save()
                    ctx.translate(p.x, p.y)
                    ctx.arc(0,0,.05,.05, 2*math.pi)
                    ctx.restore()

                if ai == 0:
                    ctx.move_to(p1.x, p1.y)
                else:
                    ctx.line_to(p1.x, p1.y)
                ctx.curve_to(p2.x, p2.y, p3.x, p3.y, p4.x, p4.y)
                ctx.save()
                ctx.scale(-1, 1)
                ctx.curve_to(p3.x, p3.y, p2.x, p2.y, p1.x, p1.y)
                ctx.restore()

                ctx.restore()
                #ctx.rectangle(0, 0, 1, 1)
                #ctx.arc(0, 0,.5,0, 2*math.pi)

                #seed_shape.pre_draw(ctx)
                #seed_shape.draw_path(ctx, for_fill=True)
            ctx.close_path()
            ctx.restore()
            if border_color and i == 0:
                path = ctx.copy_path()
            else:
                path = None
            if should_fill:
                draw_fill(ctx, color)
            else:
                draw_stroke(ctx, 1, color)
            if border_color and i == 0:
                ctx.save()
                ctx.new_path()
                ctx.append_path(path)
                ctx.restore()
                draw_stroke(ctx, 2, border_color)
