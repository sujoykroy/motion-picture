from .point import Point

class Rectangle:
    IdSeed = 0

    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.id_num = Rectangle.IdSeed+1
        Rectangle.IdSeed = Rectangle.IdSeed+1

    def copy(self):
        return Rectangle(self.x1, self.y1, self.x2, self.y2)

    def copy_from(self, other):
        self.x1 = other.x1
        self.x2 = other.x2
        self.y1 = other.y1
        self.y2 = other.y2

    def to_dict(self):
        return dict(x1=self.x1, x2=self.x2, y1=self.y1, y2=self.y2)

    def to_array(self):
        return [self.x1, self.y1, self.x2, self.y2]

    @staticmethod
    def create_from_dict(dict_rect):
        return Rectangle(
            x1=dict_rect.get("x1", 0), x2=dict_rect.get("x2", 0),
            y1=dict_rect.get("y1", 0), y2=dict_rect.get("y2", 0))

    def __eq__(self, other):
        return self.id_num == other.id_num

    def standardize(self):
        if self.x1>self.x2:
            self.x1, self.x2 = self.x2, self.x1
        if self.y1>self.y2:
            self.y1, self.y2 = self.y2, self.y1

    def get_cx(self):
        return (self.x1+self.x2)*0.5

    def get_cy(self):
        return (self.y1+self.y2)*0.5

    def set_cxy_wh(self, cx, cy, w, h):
        self.x1 = cx-w*0.5
        self.x2 = cx+w*0.5
        self.y1 = cy-h*0.5
        self.y2 = cy+h*0.5

    def set_values(self, x1=None, y1=None, x2=None, y2=None):
        if x1 is not None:
            self.x1 = x1
        if x2 is not None:
            self.x2 = x2
        if y1 is not None:
            self.y1 = y1
        if y2 is not None:
            self.y2 = y2

    def translate(self, d, sign=1):
        self.x1 += sign*d.x
        self.x2 += sign*d.x
        self.y1 += sign*d.y
        self.y2 += sign*d.y

    def scale(self, sx, sy):
        self.x1 *= sx
        self.x2 *= sx
        self.y1 *= sy
        self.y2 *= sy

    def same_scale(self, scale):
        self.x1 *= scale
        self.x2 *= scale
        self.y1 *= scale
        self.y2 *= scale

    def get_width(self):
        return abs(self.x2-self.x1)

    def get_height(self):
        return abs(self.y2-self.y1)

    @property
    def width(self):
        return abs(self.x2-self.x1)

    @width.setter
    def width(self, value):
        self.x2 = self.x1 + value

    @property
    def height(self):
        return abs(self.y2-self.y1)

    @height.setter
    def height(self, value):
        self.y2 = self.y1 + value

    def adjust_to_aspect_ratio(self, ratio):
        width = self.get_width()
        height = self.get_height()

        adjusted_height = width/ratio
        if adjusted_height<=height:
            sign = 1 if self.y1<=self.y2 else -1
            self.y2 = self.y1 + sign*adjusted_height
        else:
            adjusted_width = height*ratio
            sign = 1 if self.x1<=self.x2 else -1
            self.x2 = self.x1 + sign*adjusted_width

    def keep_x2y2_inside_bound(self, bound_rect):
        if self.x2<bound_rect.x1:
            self.x2 = bound_rect.x1
        elif self.x2>bound_rect.x2:
            self.x2 = bound_rect.x2

        if self.y2<bound_rect.y1:
            self.y2 = bound_rect.y1
        elif self.y2>bound_rect.y2:
            self.y2 = bound_rect.y2

    def keep_x1y1_inside_bound(self, bound_rect):
        x1x2diff = self.x2-self.x1

        if self.x1<bound_rect.x1:
            self.x1 = bound_rect.x1
            self.x2 = self.x1 + x1x2diff
        elif self.x2>bound_rect.x2:
            self.x2 = bound_rect.x2
            self.x1 = self.x2 - x1x2diff

        y1y2diff = self.y2-self.y1
        if self.y1<bound_rect.y1:
            self.y1 = bound_rect.y1
            self.y2 = self.y1 + y1y2diff
        elif self.y2>bound_rect.y2:
            self.y2 = bound_rect.y2
            self.y1 = self.y2 - y1y2diff

    def is_within(self, point):
        if self.x1<=self.x2:
            if point.x<self.x1 or point.x>self.x2:
                return False
        else:
            if point.x<self.x2 or point.x>self.x1:
                return False
        if self.y1<=self.y2:
            if point.y<self.y1 or point.y>self.y2:
                return False
        else:
            if point.y<self.y2 or point.y>self.y1:
                return False
        return True

    def make_integer(self):
        self.x1 = int(self.x1)
        self.x2 = int(self.x2)
        self.y1 = int(self.y1)
        self.y2 = int(self.y2)

    def get_json(self):
        return dict(x1=self.x1, y1=self.y1,
            x2=self.x2, y2=self.y2)

    @classmethod
    def create_from_json(cls, data):
        if not data:
            return None
        return Rectangle(
            x1=data["x1"], y1=data["y1"],
            x2=data["x2"], y2=data["y2"]
        )

    def __repr__(self):
        return "Rectangle(x1={0},y1={1},x2={2},y2={3})".format(self.x1, self.y1, self.x2, self.y2)
