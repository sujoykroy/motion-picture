from MotionPicture.commons import *
import math

class Drawer(object):
    def __init__(self):
        self.params = dict()
        self.fill_color = "ffff00"
        self.progress = 0

    def set_params(self, params):
        self.params = dict(params)
        self.fill_color = self.params.get("fc", self.fill_color)

    def set_progress(self, value):
        self.progress = value

    def draw(self, ctx, anchor_at):
        ctx.translate(anchor_at.x, anchor_at.y)
        ctx.scale(1./40, 1./40)
        ctx.rotate(math.pi*2*self.progress)
        ctx.rectangle(0, 0, 10, 10)
        draw_fill(ctx, self.fill_color)

drawer_klass = Drawer
