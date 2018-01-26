import math

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def assign(self, x, y):
        self.x = x
        self.y = y

    def subtract(self, other):
        self.x -= other.x
        self.y -= other.y

    def add(self, other):
        self.x += other.x
        self.y += other.y

    def scale(self, sx, sy):
        self.x *= sx
        self.y *= sy

    def copy_from(self, other):
        self.x = other.x
        self.y = other.y

    def diff(self, other):
        return Point(self.x-other.x, self.y-other.y)

    def distance(self, other):
        dx = other.x-self.x
        dy = other.y-self.y
        return math.sqrt(dx*dx+dy*dy)

    def get_in_between(self, other, frac):
        x = self.x + (other.x-self.x)*frac
        y = self.y + (other.y-self.y)*frac
        return Point(x, y)

    def get_ratio(self):
        return self.x/self.y