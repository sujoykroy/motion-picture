from .slide import Slide
from ..geom.rectangle import Rectangle
from ..geom.circle import Circle


class GeomSlide(Slide):
    TYPE_NAME = "geom"
    KEY_SCALE = "scale"
    KEY_FILL_COLOR = "fill_color"
    KEY_STROKE_COLOR = "stroke_color"
    KEY_STROKE_WIDTH = "stroke_width"

    CONSTRUCTOR_KEYS = Slide.CONSTRUCTOR_KEYS +[
        KEY_SCALE, KEY_FILL_COLOR, KEY_STROKE_COLOR, KEY_STROKE_WIDTH]

    def __init__(self, scale=1, fill_color=None, stroke_color=None, stroke_width=None, **kwargs):
        super().__init__(**kwargs)
        self.scale = scale
        self.fill_color = fill_color or "#FFFF00"
        self.stroke_color = stroke_color or "#000000"
        self.stroke_width = stroke_width or 1

class RectGeomSlide(GeomSlide):
    TYPE_NAME = "rect_geom"
    KEY_CENTER_X = "center_x"
    KEY_CENTER_Y = "center_y"
    KEY_WIDTH = "width"
    KEY_HEIGHT = "height"

    CONSTRUCTOR_KEYS = GeomSlide.CONSTRUCTOR_KEYS + [
        KEY_CENTER_X, KEY_CENTER_Y,
        KEY_WIDTH, KEY_HEIGHT
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.center_x = kwargs.get(self.KEY_CENTER_X) or 0.5
        self.center_y = kwargs.get(self.KEY_CENTER_Y) or 0.5
        self.width = kwargs.get(self.KEY_WIDTH) or 1
        self.height = kwargs.get(self.KEY_HEIGHT) or 1

    def get_vector_shape(self, width, height):
        rect = Rectangle(
            x1=width * self.center_x - width * self.width * self.scale * 0.5,
            y1=height * self.center_y - height * self.height * self.scale * 0.5,
            x2=width * self.center_x + width * self.width * self.scale * 0.5,
            y2=height * self.center_y + height * self.height * self.scale * 0.5,
        )
        return rect


class CircleGeomSlide(GeomSlide):
    TYPE_NAME = "circle_geom"
    KEY_CENTER_X = "center_x"
    KEY_CENTER_Y = "center_y"
    KEY_RADIUS = "radius"

    CONSTRUCTOR_KEYS = GeomSlide.CONSTRUCTOR_KEYS + [
        KEY_CENTER_X, KEY_CENTER_Y,
        KEY_RADIUS
    ]

    def __init__(self, center_x=0.5, center_y=0.5, radius=1, **kwargs):
        super().__init__(**kwargs)
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius

    def get_vector_shape(self, width, height):
        radius = min(width,  height) * self.radius * self.scale * 0.5
        circle = Circle(
            center_x=width * self.center_x,
            center_y=height * self.center_y,
            radius=radius
        )
        return circle
