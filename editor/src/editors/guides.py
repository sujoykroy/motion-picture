from ..commons import Color, Point
from ..commons.draw_utils import draw_stroke, draw_text
from xml.etree.ElementTree import Element as XmlElement

GUIDE_COLOR = Color.parse("0000ffaa")
GUIDE_TEXT_BACK_COLOR = Color.parse("eeeeee")
GUIDE_TEXT_BORDER_COLOR = Color.parse("000000")

class Guide(object):
    ID_SEED = 0
    TAG_NAME = "guide"

    def __init__(self):
        Guide.ID_SEED += 1
        self.id_num = Guide.ID_SEED

    def __hash__(self):
        return hash(self.id_num)

    def __eq__(self, other):
        return isinstance(other, Guide) and self.id_num == other.id_num

    def __ne__(self, other):
        return not (self == other)

    @staticmethod
    def create_from_xml_element(elm):
        elm_type = elm.attrib["type"]
        if elm_type == VerticalGuide.TYPE_NAME:
            return VerticalGuide(x=float(elm.attrib.get("x", 0)))
        elif elm_type == HorizontalGuide.TYPE_NAME:
            return HorizontalGuide(y=float(elm.attrib.get("y", 0)))


class VerticalGuide(Guide):
    TYPE_NAME = "vertical"

    def __init__(self, x, parent_shape=None):
        Guide.__init__(self)
        self.x = x
        self.parent_shape = parent_shape
        self.saved_x = x

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["type"] = self.TYPE_NAME
        elm.attrib["x"] = "{0}".format(self.x)
        return elm

    def save_position(self):
        self.saved_x = self.x

    def draw(self, ctx, out_width, out_height):
        point = Point(self.x, 0)
        point = self.parent_shape.reverse_transform_point(point)
        ctx.move_to(point.x, 0)
        ctx.line_to(point.x, out_height)
        draw_stroke(ctx, 2, GUIDE_COLOR)

        text = "{0:.02f}".format(self.x)
        draw_text(ctx, text, x=point.x+2.5, y=point.y-2,
            align="bottom-center", font_name = "8", padding=2,
            back_color=GUIDE_TEXT_BACK_COLOR, border_color=GUIDE_TEXT_BORDER_COLOR)

    def is_within(self, point):
        return abs(point.x-self.x)<5

    def move(self, point):
        self.x = self.saved_x + point.x

class HorizontalGuide(Guide):
    TYPE_NAME = "horizontal"

    def __init__(self, y, parent_shape=None):
        Guide.__init__(self)
        self.y = y
        self.parent_shape = parent_shape
        self.saved_y = y

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["type"] = self.TYPE_NAME
        elm.attrib["y"] = "{0}".format(self.y)
        return elm

    def save_position(self):
        self.saved_y = self.y

    def draw(self, ctx, out_width, out_height):
        point = Point(0, self.y)
        point = self.parent_shape.reverse_transform_point(point)
        ctx.move_to(0, point.y)
        ctx.line_to(out_width, point.y)
        draw_stroke(ctx, 2, GUIDE_COLOR)

        text = "{0:.02f}".format(self.y)
        draw_text(ctx, text, x=point.x-5, y=point.y+3,
            align="right", font_name = "8", padding=2,
            back_color=GUIDE_TEXT_BACK_COLOR, border_color=GUIDE_TEXT_BORDER_COLOR)

    def is_within(self, point):
        return abs(point.y-self.y)<5

    def move(self, point):
        self.y = self.saved_y + point.y
