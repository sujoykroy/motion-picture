from .point import Point

class Circle:
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius

    def to_array(self):
        return [
            self.x1,
            self.y1,
            self.x2,
            self.y2,
        ]

    @property
    def width(self):
        return 2 * self.radius

    @property
    def height(self):
        return 2 * self.radius

    @property
    def x1(self):
        return self.center_x - self.radius

    @property
    def y1(self):
        return self.center_y - self.radius

    @property
    def x2(self):
        return self.center_x + self.radius

    @property
    def y2(self):
        return self.center_y + self.radius
