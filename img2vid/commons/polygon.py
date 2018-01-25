from .point import Point

class Polygon:
    def __init__(self, points):
        self.points = list(points)
        self.lengths = []
        self.length = 0
        self.calculate_lengths()

    def calculate_lengths(self):
        del self.lengths[:]
        total_length = 0
        for i in range(1, len(self.points)):
            length = self.points[i].distance(self.points[i-1])
            total_length += length
            self.lengths.append(length)
        self.length = total_length

    def get_point_at(self, frac):
        l = frac*self.length
        elapsed = 0
        index = 0
        for i in range(len(self.lengths)):
            if elapsed+self.lengths[i]<=l:
                index = i
                break
            elapsed += self.lengths[i]
        return self.points[index].get_in_between(self.points[index+1], frac)

    def serialize(self):
        data = dict(points=[])
        for point in self.points:
            data["points"].append(dict(x=point.x, y=point.y))
        return data

    @classmethod
    def create_from_data(cls, data):
        points = []
        for point in data["points"]:
            point = Point(point.x, ppoint.y)
            points.append(point)
        return cls(points)

    @classmethod
    def create_from_data(cls, data):
        points = []
        for point in data["points"]:
            point = Point(point["x"], point["y"])
            points.append(point)
        return cls(points)