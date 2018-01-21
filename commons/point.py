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

    def copy_from(self, other):
        self.x = other.x
        self.y = other.y

    def diff(self, other):
        return Point(self.x-other.x, self.y-other.y)