import random

from .point import Point
from .rectangle import Rectangle
from .polygon import Polygon

class ScalePan:
    def __init__(self, scale_start, scale_end, pan_polygon):
        self.scale_start = scale_start
        self.scale_end = scale_end
        self.pan_polygon = pan_polygon

    def get_view_rect(self, frac, bound_width=1, bound_height=1, aspect_ratio=1):
        scale = self.scale_start + (self.scale_end-self.scale_start)*frac
        view_width = int(round(bound_width*scale))
        view_height = int(round(view_width/aspect_ratio))
        center = Point(view_width*0.5, view_height*0.5)

        point = self.pan_polygon.get_point_at(frac)
        point.scale(bound_width-2*center.x, bound_height-2*center.y)
        point.add(center)
        rect= Rectangle(
            point.x-view_width*0.5, point.y-view_height*0.5,
            point.x+view_width*0.5, point.y+view_height*0.5)

        return rect

    def get_polygon_points(self, bound_width=1, bound_height=1, aspect_ratio=1):
        points = []
        for i in range(bound_width):
            frac = i/bound_width
            rect = self.get_view_rect(frac, bound_width, bound_height, aspect_ratio)
            points.append(Point(rect.get_cx(), rect.get_cy()))
        return points

    def serialize(self):
        data = dict(scale_start=self.scale_start,
                    scale_end=self.scale_end,
                    pan_polygon=self.pan_polygon.serialize())
        return data

    @classmethod
    def create_from_data(cls, data):
        pan_polygon = Polygon.create_from_data(data["pan_polygon"])
        return cls(data["scale_start"], data["scale_end"], pan_polygon)

    @classmethod
    def create_random(cls, min_point_count, max_point_count):
        points = []
        random.seed()
        point_count = int(min_point_count+(max_point_count-min_point_count)*random.random())
        if point_count<2:
            point_count = 2

        for i in range(point_count):
            random.seed()
            point = Point(random.random(), random.random())
            if i>0:
                while(point.distance(points[-1])<0.5):
                    point = Point(random.random(), random.random())
            points.append(point)

        scale_start = 0.5 - random.random()*0.5
        scale_end = 0.5 + random.random()*0.5
        random.seed()
        if random.choice([True, False]):
            scale_start, scale_end = scale_end, scale_start
        return ScalePan(scale_start, scale_end, Polygon(points))