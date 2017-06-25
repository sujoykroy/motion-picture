from rectangle_shape import RectangleShape
from ..commons import *
import parser

class CustomShape(RectangleShape):
    TYPE_NAME = "custom"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius):
        super(CustomShape, self).__init__(
                anchor_at, border_color, border_width,
                                fill_color, width, height, corner_radius)
        self.code_path = None
        self.progress = 0
        self.params = None
        self.drawer = None

    def copy(self, copy_name=False, deep_copy=False):
        newob = CustomShape(self.anchor_at.copy(), copy_value(self.border_color), self.border_width,
                             copy_value(self.fill_color), self.width, self.height, self.corner_radius)
        self.copy_into(newob, copy_name)
        newob.set_code_path(self.code_path)
        newob.set_params(self.params)
        newob.set_progress(self.progress)
        return newob

    def get_xml_element(self):
        elm = RectangleShape.get_xml_element(self)
        elm.attrib["code_path"] = self.code_path
        elm.attrib["progress"] = "{0}".format(self.progress)
        if self.params:
            elm.attrib["params"] = self.params
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        shape = super(CustomShape, cls).create_from_xml_element(elm)
        shape.set_code_path(elm.attrib.get("code_path"))
        shape.set_progress (float(elm.attrib.get("progress")))
        shape.set_params(elm.attrib.get("params", ""))
        return shape

    def set_code_path(self, filepath):
        self.code_path = filepath
        if not os.path.isfile(filepath):
            return
        f = open(filepath)
        source = f.read()
        f.close()
        code = compile(source, filepath, 'exec')
        local_vars = dict(drawer_klcass=None)
        exec(code, globals(), local_vars)
        drawer_klass = local_vars.get("drawer_klass")
        if drawer_klass:
            self.drawer = drawer_klass()

    def set_params(self, params):
        self.params = params
        if self.drawer:
            try:
                params_obj = eval(parser.expr("dict({0})".format(params)).compile())
            except:
                params_obj = dict()
            self.drawer.set_params(params_obj)

    def set_progress(self, value):
        self.progress = value
        if self.drawer:
            self.drawer.set_progress(self.progress)

    def draw(self, ctx, drawing_size=None, fixed_border=True, root_shape=None, pre_matrix=None):
        self.fill_shape_area(ctx, root_shape=root_shape)

        if self.drawer:
            custom_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(drawing_size.x), int(drawing_size.y))
            custom_ctx = cairo.Context(custom_surface)
            if pre_matrix:
                custom_ctx.set_matrix(pre_matrix)
            self.pre_draw(custom_ctx, root_shape=root_shape)
            custom_ctx.scale(self.width, self.height)
            anchor_at_scaled = self.anchor_at.copy()
            anchor_at_scaled.scale(1./self.width, 1./self.height)
            self.drawer.draw(custom_ctx, anchor_at_scaled)

            orig_mat = ctx.get_matrix()
            ctx.set_matrix(cairo.Matrix())
            ctx.set_source_surface(custom_surface)
            ctx.set_matrix(orig_mat)

            ctx.save()
            self.pre_draw(ctx, root_shape=root_shape)
            self.draw_path(ctx)
            ctx.clip()
            ctx.paint()
            ctx.restore()

        self.storke_shape_area(ctx, fixed_border=fixed_border, root_shape=root_shape)
