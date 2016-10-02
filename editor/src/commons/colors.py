import cairo
from point import Point

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

class GradientColor1(object):
    def __init__(self):
        self.colors = []
        self.positions = []

    def add_color_at(self, position, color):
        self.colors.append(color)
        self.positions.append(position)

    def get_pattern(self, x0, y0, x1, y1):
        pat = cairo.LinearGradient(x0, y0, x1, y1)
        for i in range(len(self.colors)):
            color = self.colors[i]
            pat.add_color_stop_rgba (self.positions[i], color.red, color.green, color.blue, color.alpha)
        return pat

    @classmethod
    def simple(cls, colors, positions=None):
        grad = cls()
        for i in range(len(colors)):
            color = colors[i]
            if type(color) is str:
                color = Color.from_html(color)
            if positions:
                position = positions[i]
            else:
                position = i*1.0/len(colors)
            grad.add_color_at(position, color)
        return grad

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

class LinearGradientColor(GradientColor):
    def build_base_cairo_pattern(self):
        return cairo.LinearGradient(
                self.color_points[0].point.x, self.color_points[0].point.y,
                self.color_points[-1].point.x, self.color_points[-1].point.y)


    @classmethod
    def create_default(cls, rect):
        newob = cls([])
        newob.color_points.append(
            ColorPoint(Color(0, 0, 0, 0), Point(rect.left+rect.width*.5, rect.top+rect.height*.5)))
        newob.color_points.append(
            ColorPoint(Color(0, 0, 0, 1), Point(rect.left+rect.width, rect.top+rect.height)))
        return newob

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
