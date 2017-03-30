from ..commons import *
from shape import Shape


class CameraShape(Shape):
    TYPE_NAME = "camera"
    EYE_TYPE_RECTANGLE = 0
    EYE_TYPE_OVAL = 1

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height,
                       aspect_ratio, eye_type):
        Shape.__init__(self, anchor_at, border_color, border_width, fill_color, width, height)
        self.set_aspect_ratio(aspect_ratio)
        self.eye_type = eye_type
        self.set_width(self.width)

    def get_xml_element(self):
        elm = Shape.get_xml_element(self)
        elm.attrib["aspect_ratio"] = self.aspect_ratio
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        arr = Shape.get_params_array_from_xml_element(elm)
        arr.append(elm.attrib.get("aspect_ratio", "1:1"))
        arr.append(elm.attrib.get("eye_type", CameraShape.EYE_TYPE_RECTANGLE))
        shape = cls(*arr)
        shape.assign_params_from_xml_element(elm)
        return shape

    def copy(self, copy_name=False, deep_copy=False):
        newob = CameraShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                            self.fill_color.copy(), self.width, self.height,
                            self.aspect_ratio, self.eye_type)
        self.copy_into(newob, copy_name)
        return newob

    def draw_image(self, ctx):
        if self.linked_to:
            cam_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(self.width), int(self.height))
            cam_ctx = cairo.Context(cam_surface)

            outline = self.linked_to.get_abs_outline(0)
            sx = self.width/self.linked_to.width
            sy = self.height/self.linked_to.height
            cam_ctx.scale(sx, sy)

            translation = self.linked_to.parent_shape.translation
            cam_ctx.translate(-translation.x, -translation.y)

            translation = self.linked_to.translation
            cam_ctx.translate(-translation.x, -translation.y)

            parent_shape = self.linked_to.parent_shape
            parent_parent_shape = parent_shape.parent_shape
            parent_shape.parent_shape = None
            parent_shape.draw(cam_ctx)
            parent_shape.parent_shape = parent_parent_shape

            ctx.set_source_surface(cam_surface)
            ctx.clip()
            ctx.paint()
            return
        ctx.save()
        ctx.translate(0, -self.CAMERA_ICON.get_abs_outline(0).height*1.2)
        self.CAMERA_ICON.draw(ctx)
        ctx.restore()

    def draw_path(self, ctx, for_fill=False):
        if self.eye_type == CameraShape.EYE_TYPE_OVAL:
            draw_oval(self, ctx, self.width, self.height)
        else:
            draw_rounded_rectangle(ctx, 0, 0, self.width, self.height, 0)

    def set_aspect_ratio(self, value):
        width, height = value.split(":")
        self._aspect_ratio = float(width)/float(height)
        self.aspect_ratio = value
        self.set_width(self.width)

    def set_width(self, value):
        self.width = value
        self.height = value/self._aspect_ratio

    def set_height(self, value):
        self.height = value
        self.width = self.height*self._aspect_ratio
