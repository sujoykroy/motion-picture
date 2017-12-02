from point import Point

class Rect(object):
    def __init__(self, left, top, width, height, corner_radius=0):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.corner_radius = corner_radius

    def copy(self):
        return Rect(left=self.left, top=self.top, width=self.width, height=self.height)

    def expand_include(self, other):
        if other is None: return
        x1, y1 = self.left, self.top
        x2, y2 = self.left+self.width, self.top+self.height
        x3, y3 = other.left, other.top
        x4, y4 = other.left+other.width, other.top+other.height
        self.left = min(x1, x2, x3, x4)
        self.top = min(y1, y2, y3, y4)
        self.width = max(x1, x2, x3, x4)-self.left
        self.height = max(y1, y2, y3, y4)-self.top

    def __repr__(self):
        return "Rect(left={0}, top={1}, width={2}, height={3})".format(
                self.left, self.top, self.width, self.height)

    def scale(self, sx, sy):
        self.left *= sx
        self.top *= sy
        self.width *= sx
        self.height *= sy

    def translate(self, dx, dy):
        self.left += dx
        self.top += dy

    @classmethod
    def create_from_points(cls, *points):
        x0, y0 = points[0].x, points[0].y
        x1, y1 = points[1].x, points[1].y
        width = abs(x1-x0)
        height = abs(y1-y0)
        return cls(min(x0, x1), min(y0, y1), width, height)
