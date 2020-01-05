from gi.repository import Gtk
from ..commons import *

class MeterBar(Gtk.DrawingArea):
    def __init__(self):
        Gtk.DrawingArea.__init__(self)
        self.connect("draw", self.on_draw)
        self.fraction = 0.5
        self.text = ""
        self.props.margin = 2

    def set_fraction(self, fraction):
        self.fraction = fraction
        self.queue_draw()

    def set_text(self, text):
        self.text = text
        self.queue_draw()

    def on_draw(self, widget, ctx):
        ww = widget.get_allocated_width()
        wh = widget.get_allocated_height()
        ww -= 2*self.props.margin
        wh -= 2*self.props.margin
        set_default_line_style(ctx)
        #ctx.set_antialias(True)
        ctx.translate(self.props.margin, self.props.margin)

        draw_rounded_rectangle(ctx, 0, 0, ww, wh, r=2)
        draw_fill(ctx, "FFFFFF")

        draw_rounded_rectangle(ctx, 0, 0, ww*self.fraction, wh, r=2)
        draw_fill(ctx, "00FF00")

        draw_rounded_rectangle(ctx, 0, 0, ww, wh, r=2)
        draw_stroke(ctx, 1, "000000")
        draw_rounded_rectangle(ctx, 0, 0, ww*self.fraction, wh, r=2)
        draw_stroke(ctx, 1, "000000")

        if self.text:
            draw_text(ctx, x=0, y=wh, align="bottom", padding=2,
                      width=ww, fit_width=True,
                      text=self.text, text_color="000000")

