import cairo

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
        if text is None: return None
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

class GradientColor(object):
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


