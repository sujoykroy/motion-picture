import cairo
from point import Point
from texture_map_color import *

class Color(object):
    def __init__(self, red, green, blue, alpha):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def copy(self):
        return Color(self.red, self.green, self.blue, self.alpha)

    def get_array(self):
        return [self.red, self.green, self.blue, self.alpha]

    def copy_from(self, color):
        if not isinstance(color, Color): return
        self.red = color.red
        self.green = color.green
        self.blue = color.blue
        self.alpha = color.alpha

    def to_text(self):
        return "{0},{1},{2},{3}".format(self.red, self.green, self.blue, self.alpha)

    def to_html(self):
        arr = [self.red, self.green, self.blue, self.alpha]
        for i in range(len(arr)):
            arr[i] = hex(int(arr[i]*255))[2:]
            if len(arr[i]) == 1:
                arr[i] = "0" + arr[i]
        return "#" + "".join(arr)

    def set_inbetween(self, start_color, end_color, frac):
        if not isinstance(start_color, Color) or not isinstance(end_color, Color):
            return
        self.red = start_color.red + (end_color.red-start_color.red)*frac
        self.green = start_color.green + (end_color.green-start_color.green)*frac
        self.blue = start_color.blue + (end_color.blue-start_color.blue)*frac
        self.alpha = start_color.alpha + (end_color.alpha-start_color.alpha)*frac

    @classmethod
    def from_text(cls, text):
        if text is None or text == "None": return None
        r, g, b, a = text.split(",")
        return cls(float(r), float(g), float(b), float(a))

    @classmethod
    def from_html(cls, html):
        arr = []
        for i in range(0, len(html), 2):
            arr.append(int(html[i:i+2], 16)/255.)
        if len(arr)<4:
            arr.append(1.)
        return Color(*arr)

    @classmethod
    def parse(cls, color):
        if isinstance(color, Color):
            return color
        elif isinstance(color, str):
            return Color.from_html(color)
        else:
            return color

class ColorPoint(object):
    def __init__(self, color, point):
        self.color = color
        self.point = point

class GradientColor(object):
    def __init__(self, color_points):
        self.color_points = list(color_points)
        self.pattern = None
        self.get_pattern()

    def copy(self):
        newob = LinearGradientColor([])
        for color_point in self.color_points:
            color_point = ColorPoint(color_point.color.copy(), color_point.point.copy())
            newob.color_points.append(color_point)
        newob.get_pattern()
        return newob

    def copy_from(self, other):
        if not isinstance(other, GradientColor):
            return
        for i in range(min(len(other.color_points), len(self.color_points))):
            self.color_points[i].point.copy_from(other.color_points[i].point)
            self.color_points[i].color.copy_from(other.color_points[i].color)
        self.pattern = None

    def set_inbetween(self, start_color, end_color, frac):
        if not isinstance(start_color, GradientColor) or not isinstance(end_color, GradientColor):
            return

        for i in range(min(len(start_color.color_points), \
                           len(end_color.color_points), len(self.color_points))):
            self.color_points[i].point.set_inbetween(
                    start_color.color_points[i].point,
                    end_color.color_points[i].point, frac
            )
            self.color_points[i].color.set_inbetween(
                    start_color.color_points[i].color,
                    end_color.color_points[i].color, frac
            )
        self.pattern = None

    def to_text(self):
        arr = []
        for color_point in self.color_points:
            text = "{0};{1}".format(color_point.color.to_text(), color_point.point.to_text())
            arr.append(text)
        text = ";".join(arr)
        return self.COLOR_TYPE_NAME + ":" + text

    def insert_color_point_at(self, index, color, point):
        color_point = ColorPoint(color, point)
        self.color_points.insert(index, color_point)
        self.get_pattern(forced=True)

    def remove_color_point_at(self, color_point_index):
        del self.color_points[color_point_index]
        self.get_pattern(forced=True)

    def get_full_distance(self):
        return self.color_points[-1].point.distance(self.color_points[0].point)

    def get_distance_of(self, index):
        return self.color_points[index].point.distance(self.color_points[0].point)

    def build_base_cairo_pattern(self):
        return None

    def get_pattern(self, forced=False):
        if not self.color_points:
            return None
        if self.pattern and not forced:
            return self.pattern
        full_distance = self.get_full_distance()
        self.pattern = self.build_base_cairo_pattern()
        for color_point in self.color_points:
            frac_pos = color_point.point.distance(self.color_points[0].point)/full_distance
            color = color_point.color
            self.pattern.add_color_stop_rgba (
                frac_pos, color.red, color.green, color.blue, color.alpha)
        return self.pattern

    @classmethod
    def from_text(cls, text):
        arr = text.split(";")
        ob = cls([])
        for i in range(0, len(arr), 2):
            color = Color.from_text(arr[i])
            point = Point.from_text(arr[i+1])
            ob.color_points.append(ColorPoint(color, point))
        return ob

class LinearGradientColor(GradientColor):
    COLOR_TYPE_NAME = "linear"

    def build_base_cairo_pattern(self):
        return cairo.LinearGradient(
                self.color_points[0].point.x, self.color_points[0].point.y,
                self.color_points[-1].point.x, self.color_points[-1].point.y)

    @classmethod
    def create_default(cls, rect):
        newob = cls([])
        newob.color_points.append(
            ColorPoint(Color(0, 0, 0, 0), Point(rect.left, rect.top)))
        newob.color_points.append(
            ColorPoint(Color(0, 0, 0, 1), Point(rect.left+rect.width, rect.top+rect.height)))
        return newob

    def get_pattern_for(self, x0, y0, x1, y1):
        pattern = cairo.LinearGradient(x0, y0, x1, y1)
        full_distance = self.get_full_distance()
        for color_point in self.color_points:
            frac_pos = color_point.point.distance(self.color_points[0].point)/full_distance
            color = color_point.color
            pattern.add_color_stop_rgba (frac_pos, color.red, color.green, color.blue, color.alpha)
        return pattern

    @classmethod
    def simple_horiz(cls, colors):
        grad = cls([])
        for i in range(len(colors)):
            color = colors[i]
            if type(color) is str:
                color = Color.from_html(color)
            point = Point(i*1.0/len(colors), 0)
            color_point = ColorPoint(color, point)
            grad.color_points.append(color_point)
        return grad

class RadialGradientColor(GradientColor):
    COLOR_TYPE_NAME = "radial"

    def build_base_cairo_pattern(self):
        radius = self.get_full_distance()
        return cairo.RadialGradient(
                    self.color_points[0].point.x, self.color_points[0].point.y, 1,
                    self.color_points[0].point.x, self.color_points[0].point.y,
                    radius)

    @classmethod
    def create_default(cls, rect):
        newob = cls([])
        newob.color_points.append(
            ColorPoint(Color(0, 0, 0, 0), Point(rect.left+rect.width*.5, rect.top+rect.height*.5)))
        newob.color_points.append(
            ColorPoint(Color(0, 0, 0, 1), Point(rect.left+rect.width, rect.top+rect.height)))
        return newob

def color_from_text(text):
    if not text:
        return None
    arr = text.split(":")
    if len(arr) == 1:
        return Color.from_text(arr[0])
    color_type = arr[0]
    if color_type == LinearGradientColor.COLOR_TYPE_NAME:
        return LinearGradientColor.from_text(arr[1])
    elif color_type == RadialGradientColor.COLOR_TYPE_NAME:
        return RadialGradientColor.from_text(arr[1])
    elif color_type == TextureMapColor.COLOR_TYPE_NAME:
        return TextureMapColor.from_text(arr[1])

def color_copy(color):
    if color is None:
        return None
    return color.copy()
