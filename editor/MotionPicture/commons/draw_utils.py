from .colors import *
from .rect import Rect
import  cairo, math
from gi.repository import Pango, PangoCairo

def set_default_line_style(ctx):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

def set_ctx_color(ctx, color):
    if isinstance(color, tuple):
        ctx.set_source_rgba(*color)
    elif isinstance(color, Color):
        ctx.set_source_rgba(*color.get_array())
    elif isinstance(color, str):
        ctx.set_source_rgba(*Color.from_html(color).get_array())
    elif isinstance(color, GradientColor):
        ctx.set_source(color.get_pattern())
    elif isinstance(color, ImageColor):
        pattern = ctx.set_source_surface(color.get_surface(), color.x, color.y)
        pattern.set_extend(color.get_extend_type())
    else:
        ctx.set_source(color)

def draw_stroke(ctx, line_width, color=Color(0,0,0,1)):
    ctx.save()
    if isinstance(color, Color):
        ctx.set_source_rgba(*color.get_array())
    elif isinstance(color, str):
        ctx.set_source_rgba(*Color.from_html(color).get_array())
    elif isinstance(color, GradientColor):
        ctx.set_source(color.get_pattern())
    elif isinstance(color, ImageColor):
        ctx.set_source_surface(color.get_surface(), color.x, color.y)
        ctx.get_source().set_extend(color.get_extend_type())
    else:
        ctx.set_source(color)
    ctx.set_line_width(line_width)
    ctx.stroke()
    ctx.restore()

def draw_selection_border(ctx, color=(0,0,0,1)):
    ctx.save()
    set_ctx_color(ctx, color)
    ctx.set_line_width(1)
    ctx.set_dash([5])
    ctx.stroke()
    ctx.restore()

def draw_fill(ctx, color=Color(1, 1, 1,1), even_odd=True):
    ctx.save()
    if even_odd:
        ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    else:
        ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    if isinstance(color, Color):
        ctx.set_source_rgba(*color.get_array())
    elif isinstance(color, str):
        ctx.set_source_rgba(*Color.from_html(color).get_array())
    elif isinstance(color, cairo.Pattern):
        ctx.set_source(color)
    elif isinstance(color, GradientColor):
        ctx.set_source(color.get_pattern())
    elif isinstance(color, ImageColor):
        ctx.set_source_surface(color.get_surface(), color.x, color.y)
        ctx.get_source().set_extend(color.get_extend_type())
    ctx.fill()
    ctx.restore()

def draw_rounded_rectangle(ctx, x, y, w, h, r=20):
    # This is just one of the samples from
    # http://www.cairographics.org/cookbook/roundedrectangles/
    #   A****BQ
    #  H      C
    #  *      *
    #  G      D
    #   F****E
    if r == 0:
        ctx.rectangle(x, y, w, h)
    else:
        ctx.new_path()
        ctx.move_to(x+r,y)                      # Move to A
        ctx.line_to(x+w-r,y)                    # Straight line to B
        ctx.arc(x+w-r,y+r, r, 3*math.pi/2, 4*math.pi/2)       # Curve to C, Control points are both at Q
        ctx.line_to(x+w,y+h-r)                  # Move to D
        ctx.arc(x+w-r,y+h-r, r, 0*math.pi/2, 1*math.pi/2) # Curve to E
        ctx.line_to(x+r,y+h)                    # Line to F
        ctx.arc(x+r,y+h-r, r, 1*math.pi/2, 2*math.pi/2)# Curve to G
        ctx.line_to(x,y+r)                      # Line to H
        ctx.arc(x+r,y+r, r, 2*math.pi/2, 3*math.pi/2)# Curve to A
        ctx.close_path()

def draw_straight_line(ctx, x1, y1, x2, y2):
    ctx.new_path()
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)

def draw_text(ctx, text,
              x, y, width=None, corner=5, align=None, fit_width=False, height=None, fit_height=False,
              text_color=None, back_color=None, border_color=None, border_width=1,
              padding=0, font_name=None, pre_draw=None):

    layout = PangoCairo.create_layout(ctx)
    font = Pango.FontDescription.from_string(font_name)
    layout.set_wrap(Pango.WrapMode(0))
    layout.set_font_description(font)
    layout.set_alignment(Pango.Alignment(0))

    layout.set_markup(text)

    text_rect = layout.get_pixel_extents()[1]
    l = text_rect.x
    t = text_rect.y
    w= text_rect.width
    h = text_rect.height

    l, t, w, h
    scale_x = 1
    scale_y = 1
    if width:
        if width<w:
            if fit_width:
                scale_x = width/float(w)
        else:
            layout.set_width(int(width*Pango.SCALE))
            w = width
    else:
        width = 0

    if height:
        if height<h:
            if fit_height:
                scale_y = height/float(h)
        else:
            h = height
    else:
        height = 0

    if align:
        if align.find("bottom-center")>=0:
            y -= t+h*scale_y+2*padding
        elif align.find("bottom")>=0:
            y -= -t+h*scale_x+padding
        if align.find("right")>=0:
            x -= w*scale_x+padding

    if back_color:
        ctx.save()
        if pre_draw: pre_draw(ctx)
        ctx.translate(x, y)
        ctx.scale(scale_x, scale_y)
        draw_rounded_rectangle(ctx, 0, 0, w+2*padding, h+2*padding, corner)
        ctx.restore()
        if isinstance(back_color, GradientColor):
            draw_fill(ctx, back_color.get_pattern_for(0, 0, w+2*padding, 0))
        else:
            draw_fill(ctx, back_color)

    if border_color:
        ctx.save()
        if pre_draw: pre_draw(ctx)
        ctx.translate(x, y)
        ctx.scale(scale_x, scale_y)
        draw_rounded_rectangle(ctx, 0, 0, w+2*padding, h+2*padding, corner)
        ctx.restore()
        if isinstance(border_color, GradientColor):
            draw_stroke(ctx, border_width, border_color.get_pattern(0, 0, w+2*padding, 0))
        else:
            draw_stroke(ctx, border_width, border_color)
    if not text_color:
        ctx.set_source_rgba(0,0,0,1)
    elif isinstance(text_color, Color):
        ctx.set_source_rgba(*color.get_array())
    elif isinstance(text_color, GradientColor):
        ctx.set_source(text_color.get_pattern_for(0, 0, w+2*padding, 0))
    elif type(text_color) is str:
        ctx.set_source_rgba(*Color.from_html(text_color).get_array())

    ctx.save()
    if pre_draw: pre_draw(ctx)
    ctx.translate(x, y)

    ctx.move_to(padding, padding)
    ctx.scale(scale_x, scale_y)
    PangoCairo.show_layout(ctx, layout)
    ctx.restore()

    return Rect(x, y, w+2*padding, h+2*padding)

def draw_curve(ctx, curve):
    ctx.save()
    ctx.new_path()
    ctx.move_to(curve.origin.x, curve.origin.y)
    for bezier_point in curve.bezier_points:
        ctx.curve_to(
            bezier_point.control_1.x, bezier_point.control_1.y,
            bezier_point.control_2.x, bezier_point.control_2.y,
            bezier_point.dest.x, bezier_point.dest.y)
    ctx.restore()

def draw_sine_wave(ctx, period, amplitude, phase, duration):
    cycle_count = int(math.ceil(duration*1./period)) + 1
    curve = Curve(origin=Point(0, 0))
    frac = .5
    for i in range(cycle_count):
        curve.add_bezier_point(BezierPoint(
            control_1 = Point(i*period+period*.5*frac, 0),
            control_2 = Point(i*period+period*.5*frac, -amplitude),
            dest = Point(i*period+period*.5, -amplitude)))
        curve.add_bezier_point(BezierPoint(
            control_1 = Point(i*period+period*.5*(1+frac), -amplitude),
            control_2 = Point(i*period+period*.5*(1+frac), 0),
            dest = Point(i*period+period, 0)))
    ctx.save()
    ctx.translate(0, amplitude*.5)
    ctx.translate(-period*.75-period*phase/360., 0)
    curve.draw_path(ctx)
    ctx.restore()

def draw_oval(ctx, width, height, sweep_angle=360.):
    ctx.new_path()
    ctx.save()
    ctx.translate(width*.5, height*.5)
    ctx.scale(width, height)

    if sweep_angle != 360:
        ctx.move_to(0,0)
    else:
        ctx.move_to(.5,0)
    ctx.arc(0,0,.5,0, sweep_angle*math.pi/180.)
    ctx.close_path()
    ctx.restore()


def draw_regular_convex_polygon(ctx, x, y, width, height, edges):
    edges = int(edges)
    ctx.new_path()
    ctx.save()
    ctx.translate(width*.5, height*.5)
    radius = min(width, height) /2
    angle = 360/edges
    first_px = None
    first_py = None
    for i in range(edges):
        px = radius * math.cos(i*angle * math.pi/180)
        py = radius * math.sin(i*angle * math.pi/180)
        if i == 0:
            first_px = px
            first_py = py
            ctx.move_to(px, py)
        else:
            ctx.line_to(px, py)
    ctx.close_path()
    ctx.restore()