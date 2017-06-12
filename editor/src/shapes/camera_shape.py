from ..commons import *
from shape import Shape


class CameraShape(Shape):
    TYPE_NAME = "camera"
    EYE_TYPE_RECTANGLE = 0
    EYE_TYPE_OVAL = 1
    CAMERA_ICON = None

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
        newob = CameraShape(self.anchor_at.copy(), copy_value(self.border_color), self.border_width,
                            copy_value(self.fill_color), self.width, self.height,
                            self.aspect_ratio, self.eye_type)
        self.copy_into(newob, copy_name)
        return newob

    def draw_image(self, ctx, fixed_border=True, exclude_camera_list=None):
        if self.linked_to:
            sx = self.width/self.linked_to.width
            sy = self.height/self.linked_to.height
            ctx.scale(sx, sy)
            cam_scale = max(self.parent_shape.width/self.width, self.parent_shape.height/self.height)
            if exclude_camera_list:
               exclude_camera_list = exclude_camera_list + [self]
            else:
                exclude_camera_list = [self]
            self.linked_to.paint_screen(ctx,
                      screen_width=self.linked_to.width, screen_height=self.linked_to.height,
                      cam_scale=cam_scale, fixed_border=fixed_border,
                      exclude_camera_list=exclude_camera_list)
            return
        if self.CAMERA_ICON:
            ctx.save()
            ctx.translate(0, -self.CAMERA_ICON.get_abs_outline(0).height*1.2)
            self.CAMERA_ICON.draw(ctx)
            ctx.restore()

    def paint_screen(self, ctx, screen_width, screen_height, cam_scale, fixed_border=True,
                                exclude_camera_list=None):
        cam_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                    int(self.width*cam_scale), int(self.height*cam_scale))
        cam_ctx = cairo.Context(cam_surface)
        cam_ctx.scale(cam_scale, cam_scale)

        parent_shape = self.parent_shape
        self.reverse_pre_draw(cam_ctx, root_shape=parent_shape)
        if exclude_camera_list:
            exclude_camera_list = exclude_camera_list + [self]
        else:
            exclude_camera_list = [self]
        parent_shape.draw(cam_ctx, root_shape=parent_shape, fixed_border=fixed_border,
                          no_camera=False, exclude_camera_list=exclude_camera_list)

        ctx.save()
        sx = screen_width/self.width
        sy = screen_height/self.height
        scale = min(sx, sy)
        ctx.translate((screen_width-scale*self.width)*.5, (screen_height-scale*self.height)*.5)
        ctx.scale(scale, scale)

        self.draw_path(ctx)
        ctx.scale(1/cam_scale, 1/cam_scale)
        ctx.set_source_surface(cam_surface)
        ctx.clip()
        ctx.paint()
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

    def set_width(self, value, fixed_anchor=True):
        if value<=0:
            return
        if fixed_anchor:
            abs_anchor_at = self.get_abs_anchor_at()
            self.anchor_at.x *= float(value)/self.width
            self.anchor_at.y *= float(value)/(self.height*self._aspect_ratio)
        self.width = value
        self.height = value/self._aspect_ratio
        if fixed_anchor:
            self.move_to(abs_anchor_at.x, abs_anchor_at.y)

    def set_height(self, value, fixed_anchor=True):
        if value<=0:
            return
        if fixed_anchor:
            abs_anchor_at = self.get_abs_anchor_at()
            self.anchor_at.x *= float(value*self._aspect_ratio)/self.width
            self.anchor_at.y *= float(value)/self.height
        self.height = value
        self.width = self.height*self._aspect_ratio
        if fixed_anchor:
            self.move_to(abs_anchor_at.x, abs_anchor_at.y)
