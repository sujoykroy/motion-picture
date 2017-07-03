from MotionPicture.commons import *
import math
import numpy as np
import gizeh as gz
import moviepy.editor as mpy

#Adapted from http://zulko.github.io/blog/2014/09/20/vector-animations-with-python/

class Drawer(object):
    def __init__(self):
        self.params = dict()
        self.stroke_color = Color.from_html("000000")
        self.circle_count=10
        self.circle_radius = 10
        self.stroke_size = 1
        self.progress = 0

    def set_params(self, params):
        self.params = dict(params)
        self.stroke_color = self.params.get("stroke_color", self.stroke_color)
        self.stroke_size = self.params.get("stroke_size", self.stroke_size)
        self.circle_radius = self.params.get("circle_radius", self.circle_radius)
        self.circle_count = self.params.get("circle_count", self.circle_count)

    def set_progress(self, value):
        self.progress = value

    def draw(self, ctx, anchor_at, width, height, parent_shape):
        t = self.progress*10

        W,H = 256, 256
        DURATION = 2.0
        NDISKS_PER_CYCLE = 8
        SPEED = .05
        W,H = int(width), int(height)

        dt = 1.0*DURATION/2/NDISKS_PER_CYCLE # delay between disks
        N = int(NDISKS_PER_CYCLE/SPEED) # total number of disks
        t0 = 1.0/SPEED # indicates at which avancement to start

        surface = gz.Surface(W,H)
        for i in range(1,N):
            a = (math.pi/NDISKS_PER_CYCLE)*(N-i-1)
            r = max(0, .05*(t+t0-dt*(N-i-1)))
            center = W*(0.5+ gz.polar2cart(r,a))
            color = 3*((1.0*i/NDISKS_PER_CYCLE) % 1.0,)
            circle = gz.circle(r=0.3*W, xy = center,fill = color,
                                  stroke_width=0.01*W)
            circle.draw(surface)
        contour1 = gz.circle(r=.65*W,xy=[W/2,W/2], stroke_width=.5*W)
        contour2 = gz.circle(r=.42*W,xy=[W/2,W/2], stroke_width=.02*W,
                                stroke=(1,1,1))
        #contour1.draw(surface)
        #contour2.draw(surface)

        cs = surface._cairo_surface
        ctx.set_source_surface(
            cairo.ImageSurface.create_for_data(
                cs.get_data(), cs.get_format(), cs.get_width(), cs.get_height()))
        ctx.paint()

        step_angle = math.pi*2./self.circle_count
        circle_radius = self.circle_radius
        circle_radius = (.5+self.progress)*circle_radius
        spread_radius = min(width, height)*.5-circle_radius-self.stroke_size
        for i in range(self.circle_count):
            angle = i*step_angle
            x = spread_radius*math.cos(angle)
            y = spread_radius*math.sin(angle)
            ctx.save()
            ctx.translate(anchor_at.x, anchor_at.y)
            ctx.new_path()
            ctx.translate(x, y)
            ctx.arc(0, 0, circle_radius, 0, 2*math.pi)
            ctx.restore()
            draw_stroke(ctx, self.stroke_size, self.stroke_color)

