import cairo, numpy
from point import Point
from texture_map_color import *

class Color(object):
    def __init__(self, red, green, blue, alpha):
        self.values = numpy.array([red, green, blue, alpha]).astype("f" )

    def copy(self):
        return Color(*list(self.values))

    def get_array(self):
        return list(self.values)

    def to_array(self):
        return list(self.values)

    def to_255(self):
        return (self.values*255).astype(numpy.uint8)

    def get_gl_array_value(self):
        if not self.values.flags['C_CONTIGUOUS']:
            self.values = numpy.ascontiquousarray(self.values)
        return self.values

    def copy_from(self, color):
        if not isinstance(color, Color): return
        self.values = color.values.copy()

    def set_rgba(self, red, green, blue, alpha):
        self.values[0] = red
        self.values[1] = green
        self.values[2] = blue
        self.values[3] = alpha

    def to_text(self):
        return "{0},{1},{2},{3}".format(*list(self.values))

    def to_html(self):
        arr = list(self.values)
        for i in range(len(arr)):
            arr[i] = hex(int(arr[i]*255))[2:]
            if len(arr[i]) == 1:
                arr[i] = "0" + arr[i]
        return "#" + "".join(arr)

    def set_inbetween(self, start_color, end_color, frac):
        if not isinstance(start_color, Color) or not isinstance(end_color, Color):
            return
        self.values = start_color.values + (end_color.values-start_color.values)*frac

    @classmethod
    def from_text(cls, text):
        if text is None or text == "None": return None
        arr = text.split(",")
        if len(arr) == 1:
            return Color.from_html(text)
        else:
            r, g, b, a = arr
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
        elif isinstance(color, list):
            return Color(*color)
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
        newob = self.__class__([])
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
                frac_pos, color.values[0], color.values[1], color.values[2], color.values[3])
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
            pattern.add_color_stop_rgba (frac_pos, color.values[0], color.values[1], color.values[2], color.values[3])
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

class ImageColor(object):
    COLOR_TYPE_NAME = "img"

    EXTEND_TYPES = dict(
        none=cairo.EXTEND_NONE,
        repeat= cairo.EXTEND_REPEAT,
        reflect=cairo.EXTEND_REFLECT,
        pad=cairo.EXTEND_PAD)

    def __init__(self, filename="", shape_name="",extend_type="repeat", x=0, y=0):
        if isinstance(shape_name, str):
            shape_name = shape_name.decode("utf-8")
        self.filename = filename
        self.extend_type = extend_type
        self.shape_name = shape_name
        self.x = x
        self.y = y
        self.surface = None
        self.owner_shape = None

    def set_owner_shape(self, shape):
        self.owner_shape = shape

    def copy(self):
        newob = ImageColor(self.filename, self.shape_name, self.extend_type, self.x, self.y)
        return newob

    def get_surface(self):
        if self.shape_name and self.owner_shape:
            shape = self.owner_shape.get_interior_shape(self.shape_name)
            if shape:
                self.surface = shape.get_surface(width=shape.width, height=shape.height, padding=0)
        else:
            if not self.surface and self.filename and os.path.isfile(self.filename):
                self.surface = cairo.ImageSurface.create_from_png(self.filename)
        if not self.surface:
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
        return self.surface

    def get_pattern(self):
        return cairo.SurfacePattern(self.get_surface())

    def get_extend_type(self):
        return ImageColor.EXTEND_TYPES[self.extend_type]

    def to_text(self):
        text = "{0},{1},{2},{3},{4}".format(
            self.filename, self.shape_name, self.extend_type, self.x, self.y)
        return self.COLOR_TYPE_NAME + ":" + text

    @classmethod
    def from_text(cls, text):
        if text is None or text == "None": return None
        filename, shape_name, extend_type, x, y = text.split(",")
        x = float(x)
        y = float(y)
        return cls(filename, shape_name, extend_type, x, y)

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
    elif color_type == ImageColor.COLOR_TYPE_NAME:
        return ImageColor.from_text(arr[1])

def color_copy(color):
    if color is None:
        return None
    return color.copy()

def rgb_to_hsv(rgb):
    rgb = rgb/255.
    orig_shape = tuple(rgb.shape)
    rgb.shape = (-1,3)

    maxc = numpy.amax(rgb, axis=1)
    minc = numpy.amin(rgb, axis=1)
    mmc = (maxc == minc)

    r = rgb[:, 0]
    g = rgb[:, 1]
    b = rgb[:, 2]

    v = maxc

    s = (maxc-minc) / maxc
    s = numpy.where(mmc, 0, s)

    rc = (maxc-r) / (maxc-minc)
    gc = (maxc-g) / (maxc-minc)
    bc = (maxc-b) / (maxc-minc)

    h = 4.0+gc-rc
    h = numpy.where(r==maxc, bc-gc, h)
    h = numpy.where(g==maxc, 2.0+rc-bc, h)
    h = numpy.mod((h/6.0), 1.0)
    h = numpy.where(mmc, 0, h)

    hsv = numpy.array([h,s,v]).T
    hsv.shape = orig_shape
    return hsv

def hsv_to_rgb(hsv):
    orig_shape = tuple(hsv.shape)
    hsv.shape = (-1, 3)

    h = numpy.clip(hsv[:, 0],0,1)
    s = numpy.clip(hsv[:, 1],0,1)
    v = numpy.clip(hsv[:, 2],0,1)
    s_zeros = (s==0.0)

    i = (h*6.0).astype(numpy.int) # XXX assume int() truncates!
    f = (h*6.0) - i
    p = v*(1.0 - s)
    q = v*(1.0 - s*f)
    t = v*(1.0 - s*(1.0-f))
    i = numpy.mod(i, 6)

    r = v.copy()
    r = numpy.where(i==1, q, r)
    r = numpy.where(i==2, p, r)
    r = numpy.where(i==3, p, r)
    r = numpy.where(i==4, t, r)
    r = numpy.where(i==5, v, r)
    r = numpy.where(s_zeros, v, r)

    g = t.copy()
    g = numpy.where(i==1, v, g)
    g = numpy.where(i==2, v, g)
    g = numpy.where(i==3, q, g)
    g = numpy.where(i==4, p, g)
    g = numpy.where(i==5, p, g)
    g = numpy.where(s_zeros, v, g)

    b = p.copy()
    b = numpy.where(i==1, p, b)
    b = numpy.where(i==2, t, b)
    b = numpy.where(i==3, v, b)
    b = numpy.where(i==4, v, b)
    b = numpy.where(i==5, q, b)
    b = numpy.where(s_zeros, v, b)

    rgb = (numpy.array([r,g,b])*255).T.astype(numpy.uint8)
    rgb.shape = orig_shape
    return rgb
