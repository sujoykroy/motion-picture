from ..commons import *
import time
from xml.etree.ElementTree import Element as XmlElement

class Shape(object):
    ID_SEED = 0
    TAG_NAME = "shape"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height):
        self.anchor_at = anchor_at
        self.border_color = Color.parse(border_color)
        self.border_width = border_width
        self.fill_color = Color.parse(fill_color)
        self.width = width
        self.height= height

        self.scale_x = 1.
        self.scale_y = 1.
        self.translation = Point(0,0)
        self.angle = 0
        self.id_num = Shape.ID_SEED
        self.parent_shape = None
        self._name = self.new_name()
        Shape.ID_SEED += 1

    @classmethod
    def get_pose_prop_names(cls):
        prop_names = ["anchor_at", "border_color", "border_width", "fill_color",
                      "width", "height", "scale_x", "scale_y", "translation", "angle"]
        return prop_names

    def get_pose_prop_dict(self):
        prop_dict = dict()
        for prop_name in self.get_pose_prop_names():
            value = getattr(self, prop_name)
            if isinstance(value, Point):
                value = value.copy()
            elif isinstance(value, Color):
                value = value.copy()
            prop_dict[prop_name] = value
        return prop_dict

    def set_pose_prop_from_dict(self, prop_dict):
        for prop_name in self.get_pose_prop_names():
            if prop_name in prop_dict:
                value = prop_dict[prop_name]
                if type(value) in (str, int, float):
                    setattr(self, prop_name, prop_dict[prop_name])
                elif isinstance(value, Point):
                    self_point = getattr(self, prop_name)
                    self_point.copy_from(value)
                elif isinstance(value, Color):
                    self_color = getattr(self, prop_name)
                    self_color.copy_from(value)

    def set_transition_pose_prop_from_dict(self, start_prop_dict, end_prop_dict, frac):
        for prop_name in self.get_pose_prop_names():
            if prop_name not in start_prop_dict or prop_name not in end_prop_dict: continue
            start_value = start_prop_dict[prop_name]
            end_value = end_prop_dict[prop_name]

            if type(start_value) in (int, float):
                setattr(self, prop_name, start_value+(end_value-start_value)*frac)
            elif type(start_value) in (str, ):
                setattr(self, prop_name, start_value)
            elif isinstance(start_value, Point):
                self_point = getattr(self, prop_name)
                self_point.x = start_value.x + (end_value.x-start_value.x)*frac
                self_point.y = start_value.y + (end_value.y-start_value.y)*frac
            elif isinstance(start_value, Color):
                self_color = getattr(self, prop_name)
                self_color.red = start_value.red + (end_value.red-start_value.red)*frac
                self_color.green = start_value.green + (end_value.green-start_value.green)*frac
                self_color.blue = start_value.blue + (end_value.blue-start_value.blue)*frac
                self_color.alpha = start_value.alpha + (end_value.alpha-start_value.alpha)*frac

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["type"] = self.TYPE_NAME
        elm.attrib["name"] = self._name
        elm.attrib["anchor_at"] = self.anchor_at.to_text()
        elm.attrib["border_color"] = self.border_color.to_text()
        elm.attrib["border_width"] = "{0}".format(self.border_width)
        if self.fill_color:
            elm.attrib["fill_color"] = self.fill_color.to_text()
        elm.attrib["width"] = "{0}".format(self.width)
        elm.attrib["height"] = "{0}".format(self.height)
        elm.attrib["scale_y"] = "{0}".format(self.scale_y)
        elm.attrib["scale_x"] = "{0}".format(self.scale_x)
        elm.attrib["translation"] = self.translation.to_text()
        elm.attrib["angle"] = "{0}".format(self.angle)
        return elm

    @classmethod
    def get_params_array_from_xml_element(cls, elm):
        anchor_at_str = elm.attrib.get("anchor_at", Point(0,0).to_text())
        border_color_str = elm.attrib.get("border_color", Color(0,0,0,1).to_text())
        border_width_str = elm.attrib.get("border_width", "1")
        fill_color_str = elm.attrib.get("fill_color", None)
        width_str = elm.attrib.get("width", "1")
        height_str = elm.attrib.get("height", "1")
        arr = []
        arr.append(Point.from_text(anchor_at_str))
        arr.append(Color.from_text(border_color_str))
        arr.append(float(border_width_str))
        arr.append(Color.from_text(fill_color_str))
        arr.append(float(width_str))
        arr.append(float(height_str))
        return arr

    def assign_params_from_xml_element(self, elm):
        scale_x_str = elm.attrib.get("scale_x", "1")
        scale_y_str = elm.attrib.get("scale_y", "1")
        translation_str = elm.attrib.get("translation", Point(0,0).to_text())
        angle_str = elm.attrib.get("angle", "1")

        self.scale_x = float(scale_x_str)
        self.scale_y = float(scale_y_str)
        self.translation.copy_from(Point.from_text(translation_str))
        self.angle = float(angle_str)

        name = elm.attrib.get("name", None)
        if name:
            self._name = name.replace(".", "")

    def copy_into(self, newob, copy_name=False, all_fields=False):
        newob.translation = self.translation.copy()
        newob.angle = self.angle
        newob.scale_x = self.scale_x
        newob.scale_y = self.scale_y
        if copy_name:
            newob.name = self._name
        newob.parent_shape = self.parent_shape
        if all_fields:
            newob.anchor_at.copy_from(self.anchor_at)
            if self.border_color:
                if not newob.border_color:
                    newob.border_color = self.border_color.copy()
                else:
                    newob.border_color.copy_from(self.border_color)
            else:
                newob.border_color = None
            newob.border_width = self.border_width
            if self.fill_color:
                if not newob.fill_color:
                    newob.fill_color = self.fill_color.copy()
                else:
                    newob.fill_color.copy_from(self.fill_color)
            else:
                newob.fill_color = None
            newob.width = self.width
            newob.height = self.height

    def __hash__(self):
        return hash(self.id_num)

    def __eq__(self, other):
        return isinstance(other, Shape) and self.id_num == other.id_num

    def __ne__(self, other):
        return not (self == other)

    def get_name(self):
        return self._name

    def set_prop_value(self, prop_name, value, prop_data=None):
        set_attr_name = "set_" + prop_name
        if hasattr(self, set_attr_name):
            getattr(self, set_attr_name)(value)
        elif hasattr(self, prop_name):
            setattr(self, prop_name, value)

    def get_prop_value(self, prop_name):
        get_attr_name = "get_" + prop_name
        if hasattr(self, get_attr_name):
            return getattr(self, get_attr_name)()
        elif hasattr(self, prop_name):
            return getattr(self, prop_name)
        return None

    def set_angle(self, angle):
        rel_left_top_corner = Point(-self.anchor_at.x, -self.anchor_at.y)
        rel_left_top_corner.rotate_coordinate(-angle)
        rel_left_top_corner.scale(self.scale_x, self.scale_y)
        if self.parent_shape: #must be multi shape
            rel_left_top_corner.scale(
                    self.parent_shape.child_scale_x, self.parent_shape.child_scale_y)
        abs_anchor = self.get_abs_anchor_at()
        rel_left_top_corner.translate(abs_anchor.x, abs_anchor.y)
        self.angle = angle
        self.translation.x = rel_left_top_corner.x
        self.translation.y = rel_left_top_corner.y

    def get_angle(self):
        return self.angle

    def set_border_width(self, border_width):
        self.border_width = border_width

    def get_border_width(self):
        return self.border_width

    def set_border_color(self, color):
        self.border_color.copy_from(color)

    def get_border_color(self):
        return self.border_color

    def set_fill_color(self, color):
        self.fill_color.copy_from(color)

    def get_fill_color(self):
        return self.fill_color

    def get_width(self): return self.width

    def set_width(self, value):
        if value >0:
            self.width = value

    def get_height(self): return self.height

    def set_height(self, value):
        if value>0:
            self.height = value

    def get_anchor_x(self):
        return self.anchor_at.x

    def set_anchor_x(self, value):
        self.anchor_at.x = value

    def get_anchor_y(self):
        return self.anchor_at.y

    def set_anchor_y(self, value):
        self.anchor_at.y = value

    def move_x_to(self, x):
        self.move_to(x, self.get_abs_anchor_at().y)

    def move_y_to(self, y):
        self.move_to(self.get_abs_anchor_at().x, y)

    def set_x(self, x):
        self.move_to(x, self.get_abs_anchor_at().y)

    def set_y(self, y):
        self.move_to(self.get_abs_anchor_at().x, y)

    def get_x(self):
        return self.get_abs_anchor_at().x

    def get_y(self):
        return self.get_abs_anchor_at().y

    def get_stage_xy(self):
        xy = self.get_abs_anchor_at()
        if self.parent_shape:
            parent_anchor = self.parent_shape.anchor_at
            xy.translate(-parent_anchor.x, -parent_anchor.y)
        return xy

    def set_stage_xy(self, point):
        xy = point.copy()
        if self.parent_shape:
            parent_anchor = self.parent_shape.anchor_at
            xy.translate(parent_anchor.x, parent_anchor.y)
        self.move_to(xy.x, xy.y)

    def set_stage_x(self, x):
        xy = Point(x, self.get_abs_anchor_at().y)
        if self.parent_shape:
            xy.x += self.parent_shape.anchor_at.x
        self.move_to(xy.x, xy.y)

    def set_stage_y(self, y):
        xy = Point( self.get_abs_anchor_at().x, y)
        if self.parent_shape:
            xy.y += self.parent_shape.anchor_at.y
        self.move_to(xy.x, xy.y)

    def get_abs_anchor_at(self):
        abs_anchor = self.anchor_at.copy()
        abs_anchor.rotate_coordinate(-self.angle)
        abs_anchor.scale(self.scale_x, self.scale_y)
        if self.parent_shape: #must be multi shape
            abs_anchor.scale(self.parent_shape.child_scale_x, self.parent_shape.child_scale_y)
        abs_anchor.translate(self.translation.x, self.translation.y)
        return abs_anchor

    def move_to(self, x, y):
        point = Point(x,y)
        abs_anchor_at = self.get_abs_anchor_at()
        point.translate(-abs_anchor_at.x, -abs_anchor_at.y)
        self.translation.x += point.x
        self.translation.y += point.y

    def transform_point(self, point):
        point = Point(point.x, point.y)
        abs_anchor_at = self.get_abs_anchor_at()
        point.translate(-abs_anchor_at.x, -abs_anchor_at.y)
        if self.parent_shape: #must be multi shape
            point.scale(1./self.parent_shape.child_scale_x, 1./self.parent_shape.child_scale_y)
        point.scale(1./self.scale_x, 1./self.scale_y)
        point.rotate_coordinate(self.angle)
        point.translate(self.anchor_at.x, self.anchor_at.y)
        return point

    def reverse_transform_point(self, point):
        point = Point(point.x, point.y)
        point.translate(-self.anchor_at.x, -self.anchor_at.y)
        point.rotate_coordinate(-self.angle)
        point.scale(self.scale_x, self.scale_y)
        if self.parent_shape: #must be multi shape
            point.scale(self.parent_shape.child_scale_x, self.parent_shape.child_scale_y)
        abs_anchor = self.get_abs_anchor_at()
        point.translate(abs_anchor.x, abs_anchor.y)
        return point

    def pre_draw(self, ctx):
        if self.parent_shape:
            self.parent_shape.pre_draw(ctx)
        ctx.translate(self.translation.x, self.translation.y)
        if self.parent_shape: #must be multi shape
            ctx.scale(self.parent_shape.child_scale_x, self.parent_shape.child_scale_y)
        ctx.scale(self.scale_x, self.scale_y)
        ctx.rotate(self.angle*RAD_PER_DEG)

    def draw_anchor(self, ctx):
        ctx.translate(self.anchor_at.x, self.anchor_at.y)
        ctx.arc(0, 0, 5, 0, math.pi*2)
        ctx.arc(0, 0, 2, 0, math.pi*2)

    def draw_border(self, ctx):
        if self.border_color is None: return
        ctx.set_source_rgba(*self.border_color.get_array())
        ctx.set_line_width(self.border_width)
        ctx.stroke()

    def draw_fill(self, ctx):
        if self.fill_color is None: return
        ctx.set_source_rgba(*self.fill_color.get_array())
        ctx.fill()

    def draw(self, ctx):
        if self.fill_color is not None:
            ctx.save()
            self.pre_draw(ctx)
            self.draw_path(ctx, for_fill=True)
            ctx.restore()
            self.draw_fill(ctx)

        if self.border_color is not None:
            ctx.save()
            self.pre_draw(ctx)
            self.draw_path(ctx, for_fill=False)
            ctx.restore()
            self.draw_border(ctx)

    def draw_axis(self, ctx):
        ctx.save()
        self.pre_draw(ctx)

        ctx.save()
        ctx.translate(self.anchor_at.x, self.anchor_at.y)
        ctx.set_line_width(3)

        for angle, color in [[0, "ff0000"], [90, "00ff00"]]:
            ctx.rotate(angle*RAD_PER_DEG)
            ctx.set_source_rgba(*Color.parse(color).get_array())
            ctx.move_to(0, 0)
            ctx.line_to(95, 0)
            ctx.stroke()

            ctx.move_to(100, 0)
            ctx.line_to(100-10, -5)
            ctx.line_to(100-10, 5)
            ctx.line_to(100, 0)
            ctx.fill()
        ctx.restore()

        self.draw_anchor(ctx)
        ctx.restore()
        self.draw_border(ctx)

    def get_outline(self, padding):
        return Rect(-padding, -padding, self.width+2*padding, self.height+2*padding, padding)

    def get_abs_outline(self, padding):
        outline = self.get_outline(padding)
        points = []
        points.append(Point(outline.left, outline.top))
        points.append(Point(outline.left + outline.width, outline.top))
        points.append(Point(outline.left + outline.width, outline.top + outline.height))
        points.append(Point(outline.left, outline.top + outline.height))

        abs_anchor_at = self.get_abs_anchor_at()
        min_x = max_x = min_y = max_y =  None
        for point in points:
            point = self.reverse_transform_point(point)

            if min_x is None or min_x>point.x: min_x = point.x
            if max_x is None or max_x<point.x: max_x = point.x
            if min_y is None or min_y>point.y: min_y = point.y
            if max_y is None or max_y<point.y: max_y = point.y

        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def is_within(self, point, margin=5):
        point = self.transform_point(point)
        return point.x>=-margin and point.x<=self.width+margin and \
               point.y>=-margin and point.y<=self.height+margin

    def flip(self, direction):
        pass

    NAME_SEED = 0
    @staticmethod
    def new_name():
        Shape.NAME_SEED += 1
        return "{0}_{1}".format(time.time(), Shape.NAME_SEED).replace(".", "")

    @staticmethod
    def rounded_rectangle(ctx, x, y, w, h, r=20):
        # This is just one of the samples from
        # http://www.cairographics.org/cookbook/roundedrectangles/
        #   A****BQ
        #  H      C
        #  *      *
        #  G      D
        #   F****E
        if r == 0:
            ctx.rectangle(x, y, w, h)
        else:
            ctx.move_to(x+r,y)                      # Move to A
            ctx.line_to(x+w-r,y)                    # Straight line to B
            ctx.curve_to(x+w,y,x+w,y,x+w,y+r)       # Curve to C, Control points are both at Q
            ctx.line_to(x+w,y+h-r)                  # Move to D
            ctx.curve_to(x+w,y+h,x+w,y+h,x+w-r,y+h) # Curve to E
            ctx.line_to(x+r,y+h)                    # Line to F
            ctx.curve_to(x,y+h,x,y+h,x,y+h-r)       # Curve to G
            ctx.line_to(x,y+r)                      # Line to H
            ctx.curve_to(x,y,x,y,x+r,y)             # Curve to A

    @staticmethod
    def quadrilateral(ctx, left_top, right_top, right_bottom, left_bottom):
        ctx.new_path()
        ctx.move_to(left_top.x, left_top.y)
        ctx.line_to(right_top.x, right_top.y)
        ctx.line_to(right_bottom.x, right_bottom.y)
        ctx.line_to(left_bottom.x, left_bottom.y)
        ctx.line_to(left_top.x, left_top.y)
        ctx.close_path()

    @staticmethod
    def draw_selection_border(ctx):
        ctx.save()
        ctx.set_source_rgb(0,0,0)
        ctx.set_line_width(1)
        ctx.set_dash([5])
        ctx.stroke()
        ctx.restore()

    @staticmethod
    def stroke(ctx, line_width, color=Color(0,0,0,1), dash=[]):
        ctx.save()
        ctx.set_source_rgba(*color.get_array())
        ctx.set_line_width(line_width)
        ctx.set_dash(dash)
        ctx.stroke()
        ctx.restore()


