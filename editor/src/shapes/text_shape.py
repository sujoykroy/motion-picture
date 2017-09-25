from gi.repository import Pango, PangoCairo
from ..commons import *
import cairo
from shape import Shape
from rectangle_shape import RectangleShape
import math

X_ALIGN_LEFT = 0
X_ALIGN_CENTER = 1
X_ALIGN_RIGHT = 2

Y_ALIGN_TOP = 0
Y_ALIGN_MIDDLE = 1
Y_ALIGN_BOTTOM = 2

class TextShape(RectangleShape):
    TYPE_NAME = "text"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius,
                       x_align=X_ALIGN_CENTER, y_align=Y_ALIGN_MIDDLE, text="Sample",
                       font="10", font_color=None, line_align = 1):
        if font_color is None:
            font_color = Color.parse("000000")
        RectangleShape.__init__(self, anchor_at, border_color,
                    border_width, fill_color, width, height, corner_radius)
        self.x_align = x_align
        self.y_align = y_align
        self.text = text
        self.display_text = text
        self.font = font
        self.font_color = font_color
        self.line_align = line_align
        self.exposure = 1.
        self.max_width_chars = -1
        self.character_shapes = None
        self.readjust_sizes()

    @classmethod
    def get_pose_prop_names(cls):
        prop_names = RectangleShape.get_pose_prop_names()
        prop_names.append("x_align")
        prop_names.append("y_align")
        prop_names.append("text")
        prop_names.append("font")
        prop_names.append("font_color")
        prop_names.append("line_align")
        return prop_names

    def get_xml_element(self):
        elm = RectangleShape.get_xml_element(self)
        elm.attrib["x_align"] = "{0}".format(self.x_align)
        elm.attrib["y_align"] = "{0}".format(self.y_align)
        elm.attrib["text"] = self.text
        elm.attrib["font"] = self.font
        if self.font_color:
            elm.attrib["font_color"] = self.font_color.to_text()
        elm.attrib["line_align"] = "{0}".format(self.line_align)
        elm.attrib["exposure"] = "{0}".format(self.exposure)
        elm.attrib["max_width_chars"] = "{0}".format(self.max_width_chars)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        arr = Shape.get_params_array_from_xml_element(elm)
        arr.append(float(elm.attrib.get("corner_radius", 0)))
        arr.append(int(float(elm.attrib.get("x_align", 0))))
        arr.append(int(float(elm.attrib.get("y_align", 0))))
        arr.append(elm.attrib.get("text", ""))
        arr.append(elm.attrib.get("font", ""))

        arr.append(color_from_text(elm.attrib.get("font_color", None)))
        arr.append(int(float(elm.attrib.get("line_align", 0))))
        shape = cls(*arr)
        shape.set_exposure(float(elm.attrib.get("exposure", 1.)))
        shape.set_char_width(int(float(elm.attrib.get("max_width_chars", -1))))
        shape.assign_params_from_xml_element(elm, all_fields=True)
        return shape

    def copy(self, copy_name=False, deep_copy=False):
        newob = TextShape(self.anchor_at.copy(), copy_value(self.border_color), self.border_width,
                            copy_value(self.fill_color), self.width, self.height,self.corner_radius,
                            self.x_align, self.y_align, self.text, self.font, self.font_color,
                            self.line_align)
        self.copy_into(newob, copy_name, all_fields=True)
        return newob

    def copy_into(self, newob, copy_name=False, all_fields=False):
        RectangleShape.copy_into(self, newob, copy_name=copy_name, all_fields=all_fields)
        newob.exposure = self.exposure
        newob.max_width_chars = self.max_width_chars

    def get_text_layout(self, ctx):
        layout = PangoCairo.create_layout(ctx)
        pango_font_desc = Pango.FontDescription.from_string(self.font)
        layout.set_wrap(Pango.WrapMode(0))
        layout.set_font_description(pango_font_desc)

        layout.set_markup(self.display_text)

        if (self.max_width_chars>0):
            font_size = pango_font_desc.get_size()
            if pango_font_desc.get_size_is_absolute():
                font_size *= Pango.SCALE
            layout.set_width(int(self.max_width_chars*font_size))

        text_rect = layout.get_pixel_extents()[0]
        text_width = text_rect.width
        text_height = text_rect.height
        text_left = text_rect.x
        text_top = text_rect.y

        if (self.max_width_chars>0):
            text_width = layout.get_width()*1./Pango.SCALE


        text_point_rect = layout.get_extents()[0]

        if self.max_width_chars<=0:# or self.exposure<1:
            layout.set_width(int(text_point_rect.width))

        if self.x_align == X_ALIGN_LEFT:
            x = self.border_width+self.corner_radius
        elif self.x_align == X_ALIGN_RIGHT:
            x = self.width-text_width-self.border_width-self.corner_radius
        elif self.x_align == X_ALIGN_CENTER:
            x = (self.width-text_width)*.5

        if self.y_align == Y_ALIGN_TOP:
            y = self.border_width+self.corner_radius
        elif self.y_align == Y_ALIGN_BOTTOM:
            y = self.height-text_height-self.border_width-self.corner_radius
        elif self.y_align == Y_ALIGN_MIDDLE:
            y = (self.height-text_height)*.5

        if isinstance(self.font_color, GradientColor):
            ctx.set_source(self.font_color.get_pattern())
        else:
            ctx.set_source_rgba(*self.font_color.get_array())

        layout.set_alignment(Pango.Alignment(self.line_align))

        PangoCairo.update_layout(ctx, layout)
        return layout, x-text_left, y-text_top

    def draw_text(self, ctx):
        ctx.save()

        layout, x, y = self.get_text_layout(ctx)
        ctx.move_to(x, y)
        PangoCairo.show_layout(ctx, layout)
        """
        ctx.new_path()
        ctx.translate(x, y)
        ctx.rectangle(0,0,text_width, text_height)
        draw_stroke(ctx, 1, "FF0000")
        ctx.translate(-text_left, -text_top)
        ctx.rectangle(0,0,text_width, text_height)
        draw_stroke(ctx, 1, "000000")
        """
        ctx.restore()

    def set_text(self, text):
        self.text = text
        self.readjust_sizes()

    def set_font(self, font):
        self.font = font
        self.readjust_sizes()

    def set_width(self, width, fixed_anchor=True):
        self.width = width
        self.readjust_sizes()

    def set_height(self, height, fixed_anchor=True):
        self.height = height
        self.readjust_sizes()

    def set_corner_radius(self, corner_radius):
        self.corner_radius = corner_radius
        self.readjust_sizes()

    def set_exposure(self, fraction):
        self.exposure = fraction
        length = abs(int(math.floor(len(self.text)*fraction)))
        self.display_text = self.text[0: length]

    def set_prop_value(self, prop_name, value, prop_data=None):
        if prop_name == "exposure" and prop_data and "text" in prop_data:
            self.set_text(prop_data["text"])
        super(TextShape, self).set_prop_value(prop_name, value, prop_data)

    def set_text(self, text):
        self.text = text
        self.set_exposure(self.exposure)
        self.readjust_sizes()

    def set_char_width(self, value):
        self.max_width_chars = value
        self.readjust_sizes()

    def get_char_width(self):
        return self.max_width_chars

    def calculate_text_size(self):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 320, 120)
        context = cairo.Context(surf)

        layout = PangoCairo.create_layout(context)
        pango_font_desc = Pango.FontDescription.from_string(self.font)
        layout.set_wrap(Pango.WrapMode(0))
        layout.set_font_description(pango_font_desc)

        #from "pose", line-align may become float
        layout.set_alignment(Pango.Alignment(int(self.line_align)))

        if (self.max_width_chars>0):
            layout.set_width(int(self.max_width_chars*pango_font_desc.get_size()))

        try:
            layout.set_markup(self.text)
        except:
            pass

        return layout.get_pixel_extents()[0]

    def readjust_sizes(self):
        text_rect = self.calculate_text_size()
        text_width = text_rect.width + 2*(self.border_width+self.corner_radius)
        text_height = text_rect.height + 2*(self.border_width+self.corner_radius)
        if self.width<text_width:
            self.width = text_width
        if self.height<text_height:
            self.height = text_height

    def get_private_inner_shape(self, shape_name):
        index = int(Text.parse_number(shape_name[1:-1], None))
        if index is not None:
            if not self.character_shapes:
                self.character_shapes = dict()
            if index not in self.character_shapes:
                self.character_shapes[index] = TextCharacterShape(self, index)
            return self.character_shapes[index]
        return super(TextShape, self).get_private_inner_shape(shape_name)

    def cleanup(self):
        if self.character_shapes:
            for shape in self.character_shapes.values():
                shape.cleanup()
            self.character_shapes = None
        super(TextShape, self).cleanup()

class TextCharacterShape(Shape):
    def __init__(self, parent_shape, index):
        super(TextCharacterShape, self).__init__(Point(0,0), None, 0., None, 0., 0.)
        del self.translation
        self.parent_shape = parent_shape
        self.index = index
        self._name = "_{0}_".format(self.index)

    def __getattr__(self, name):
        if name == "translation":
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 16, 16)
            ctx = cairo.Context(surf)
            layout, x, y = self.parent_shape.get_text_layout(ctx)
            if self.index<0:
                index = len(self.parent_shape.display_text)+self.index
            else:
                index = self.index
            if index<0:
                index = 0
            pango_rect = layout.index_to_pos(index)
            return Point(
                x+(pango_rect.x+pango_rect.width)*1./Pango.SCALE,
                y+(pango_rect.y+pango_rect.height)*1./Pango.SCALE)
        else:
            raise AttributeError
