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

    def __eq__(self, other):
        return self.id_num == other.id_num

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

    def translate(self, d):
        self.x1 += d.x
        self.x2 += d.x
        self.y1 += d.y
        self.y2 += d.y

    def get_width(self):
        return abs(self.x2-self.x1)

    def get_height(self):
        return abs(self.y2-self.y1)

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