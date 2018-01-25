import random

from .point import Point
from .rectangle import Rectangle
from .polygon import Polygon

class ScalePan:
    def __init__(self, scale_start, scale_end, pan_polygon):
        self.scale_start = scale_start
        self.scale_end = scale_end
        self.pan_polygon = pan_polygon

    def get_view_rect(self, frac, aspect_ratio=1):
        scale = self.scale_start + (self.scale_end-self.scale_start)*frac
        view_width = scale
        view_height = scale/aspect_ratio
        center = Point(view_width*0.5, view_height*0.5)

        point = self.pan_polygon.get_point_at(frac)
        point.scale(1-2*center.x, 1-2*center.y)
        point.add(center)
        return Rectangle(
            point.x-view_width*0.5, point.y-view_height*0.5,
            point.x+view_width*0.5, point.y+view_height*0.5)

    @classmethod
    def create_random(cls, min_point_count, max_point_count):
        points = []
        random.seed()
        point_count = int(min_point_count+(max_point_count-min_point_count)*random.random())
        if point_count<2:
            point_count = 2
        for i in range(int(point_count)):
            random.seed()
            point = Point(random.random(), random.random())
            points.append(point)
        scale_start = 1
        scale_end = random.random()
        choice = random.choice([0, 1, 2])
        if choice == 1:
            scale_start, scale_end = scale_end, scale_start
        elif choice == 2:
            scale_start = scale_end
        return ScalePan(scale_start, scale_end, Polygon(points))