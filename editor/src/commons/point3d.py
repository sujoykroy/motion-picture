import numpy

class Point3d(object):
    IdSeed = 0

    def __init__(self, x=0, y=0, z=0):
        self.values = numpy.array([x, y, z, 1], dtype='f')
        self.id_num = Point3d.IdSeed
        Point3d.IdSeed += 1

    def get_average(self):
        return (self.values[0]+self.values[1]+self.values[2])/3.

    def set_average(self, value):
        self.values[0] = value
        self.values[1] = value
        self.values[2] = value

    def __eq__(self, other):
        return isinstance(other, Point3d) and other.id_num == self.id_num

    def __hash__(self):
        return self.id_num

    def copy(self):
        return Point3d(self.values[0], self.values[1], self.values[2])

    def get_x(self):
        return self.values[0]

    def get_y(self):
        return self.values[1]

    def get_z(self):
        return self.values[2]

    def set_x(self, value):
        self.values[0] = value

    def set_y(self, value):
        self.values[1] = value

    def set_z(self, value):
        self.values[2] = value

    def multiply(self, value):
        self.values *= value
        self.values[-1] = 1

    def translate(self, point3d):
        point3d = Point3d.create_if_needed(point3d)
        self.values += point3d.values
        self.values[-1] = 1

    def assign(self, x, y, z):
        self.values[0] = x
        self.values[1] = y
        self.values[2] = z

    def to_text(self):
        return "{0},{1},{2}".format(self.values[0], self.values[1], self.values[2])

    @classmethod
    def from_text(cls, text):
        try:
            x, y, z = text.split(",")
            point = cls(float(x), float(y), float(z))
        except:
            return None
        return point

    @classmethod
    def create_if_needed(cls, data):
        if data is None or isinstance(data, Point3d):
            return data
        return Point3d(data[0], data[1], data[2])
