import cairo
from gi.repository import Gtk

class Keyboard(object):
    def __init__(self):
        self.shift_key_pressed = False
        self.control_key_pressed = False

class Text(object):
    @staticmethod
    def markup(text, **params):
        markup = "<span"
        for key, value in params.items():
            if value is None: continue
            if key in ("color", "background"):
                value = "#" + value
            markup += " {0}=\"{1}\"".format(key, value)
        markup += ">{0}</span>".format(text)
        return markup

    @staticmethod
    def label(text, **params):
        label = Gtk.Label()
        label.set_markup(Text.markup(text, **params))
        return label

def format_time(value):
    hour = int(math.floor(value / 3600.))
    value -= hour*60
    minute = int(math.floor(value / 60.))
    value -= minute*60
    value = round(value, 2)
    if hour>0:
        return "{0:02}h:{1:02}m:{2:02.2f}s".format(hour, minute, value)
    elif minute>0:
        return "{0:02}m:{1:02.2f}s".format(minute, value)
    else:
        return "{0:02.2f}s".format(value)

def copy_list(arr):
    if arr is None:
        return None
    copied_list = []
    for val in arr:
        if isinstance(val, dict):
            val = copy_dict(val)
        elif isinstance(val, list):
            val = copy_list(val)
        elif hasattr(val, "copy"):
            val = val.copy()
        copied_list.append(val)
    return copied_list

def copy_dict(dicto):
    if dicto is None:
        return None
    copied_dict = dict()
    for key, val in dicto.items():
        if isinstance(val, dict):
            val = copy_dict(val)
        elif isinstance(val, list):
            val = copy_list(val)
        elif hasattr(val, "copy"):
            val = val.copy()
        copied_dict[key] = val
    return copied_dict

class Matrix(object):
    @staticmethod
    def new(xx=1., yx=0., xy=0., yy=1., x0=0., y0=0.):
        return cairo.Matrix(xx=xx, yx=yx, yy=yy, x0=x0, y0=y0)

    @staticmethod
    def copy(matrix):
        if matrix is None: return None
        xx, yx, xy, yy, x0, y0 = matrix
        return cairo.Matrix(xx, yx, xy, yy, x0, y0)

    @staticmethod
    def interpolate(matrix1, matrix2, frac):
        values1 = [1, 0, 0, 1, 0, 0]
        values2 = [1, 0, 0, 1, 0, 0]
        values = [1, 0, 0, 1, 0, 0]
        values1[0], values1[1], values1[2], values1[3], values1[4], values1[5] = matrix1
        values2[0], values2[1], values2[2], values2[3], values2[4], values2[5] = matrix2
        for i in range(6):
            values[i] = values1[i] + (values2[i]-values1[i])*frac
        return cairo.Matrix(*values)

    @staticmethod
    def to_text(matrix):
        xx, yx, xy, yy, x0, y0 = matrix
        return "{0},{1},{2},{3},{4},{5}".format(xx, yx, xy, yy, x0, y0)

    @staticmethod
    def from_text(text):
        if text == "None":
            return None
        values = text.split(",")
        for i in range(len(values)):
            values[i] = float(values[i])
        return cairo.Matrix(*values)

class TimeLabel(object):
    def __init__(self, start, end, step, level=0):
        self.start = start
        self.end = end
        self.step = step
        self.level= level

class TimeMarker(object):
    def __init__(self, at, text):
        self.at = at
        self.text = text

    def set_text(self, text):
        text = text.strip()
        if text and len(text)>0:
            self.text =text

    def set_at(self, at):
        at = at.strip()
        if at and len(at)>0:
            try:
                at = float(at)
            except ValueError:
                return
            self.at = at

    def get_formatted_at(self):
        return "{0:02}".format(self.at)

class Span(object):
    def __init__(self, start, end, scale):
        self.start = start
        self.end = end
        self.scale = scale
