import random

from ..geom import Point, Rectangle, Polygon
from .effect import Effect

class ScalePan(Effect):
    TYPE_NAME = "scale_pan"

    KEY_TYPE = "scale_pan"
    KEY_SCALE_START = "scale_start"
    KEY_SCALE_END = "scale_end"
    KEY_PAN_POLYGON = "pan_polygon"

    def __init__(self, scale_start, scale_end, pan_polygon, **kwargs):
        super().__init__(**kwargs)
        self.scale_start = scale_start
        self.scale_end = scale_end
        self.pan_polygon = pan_polygon

    def get_rect_at(self, frac, bound_width=1, bound_height=1, aspect_ratio=1):
        scale = self.scale_start + (self.scale_end-self.scale_start)*frac
        view_width = bound_width*scale
        view_height = bound_width*scale/aspect_ratio
        center = Point(view_width*0.5, view_height*0.5)

        point = self.pan_polygon.get_point_at(frac)
        point.scale(bound_width-2*center.x, bound_height-2*center.y)
        point.add(center)
        rect = Rectangle(
            point.x-view_width*0.5, point.y-view_height*0.5,
            point.x+view_width*0.5, point.y+view_height*0.5)

        return rect

    def get_polygon_points(self, bound_width=1, bound_height=1, aspect_ratio=1):
        points = []
        for i in range(bound_width):
            frac = i/bound_width
            rect = self.get_rect_at(frac, bound_width, bound_height, aspect_ratio)
            points.append(Point(rect.get_cx(), rect.get_cy()))
        return points

    def get_json(self):
        data = super().get_json()
        data[self.KEY_SCALE_START] = self.scale_start
        data[self.KEY_SCALE_END] = self.scale_end
        data[self.KEY_PAN_POLYGON] = self.pan_polygon.get_json()
        return data

    @classmethod
    def create_from_json(cls, data):
        pan_polygon = Polygon.create_from_json(data[cls.KEY_PAN_POLYGON])
        return cls(
            data[cls.KEY_SCALE_START],
            data[cls.KEY_SCALE_END], pan_polygon)

    @classmethod
    def create_random(cls, min_point_count, max_point_count):
        points = []
        random.seed()
        point_count = int(min_point_count+\
            (max_point_count-min_point_count)*random.random())
        if point_count < 2:
            point_count = 2

        for index in range(point_count):
            random.seed()
            point = Point(random.random(), random.random())
            if index > 0:
                while point.distance(points[-1]) < 0.5:
                    point = Point(random.random(), random.random())
            points.append(point)

        scale_start = 0.5 - random.random()*0.5
        scale_end = 0.5 + random.random()*0.5
        random.seed()
        if random.choice([True, False]):
            scale_start, scale_end = scale_end, scale_start
        return ScalePan(scale_start, scale_end, Polygon(points))
