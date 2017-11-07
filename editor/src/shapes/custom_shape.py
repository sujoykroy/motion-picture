from rectangle_shape import RectangleShape
from ..commons import *
import parser
import imp
from .. import settings as Settings
from custom_props import CustomProps, CustomProp

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
        self.custom_props = CustomProps()

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
        if self.drawer:
            params_text = Text.to_text(self.drawer.params)
        else:
            params_text = ""
        elm.attrib["params"] = params_text
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        shape = super(CustomShape, cls).create_from_xml_element(elm)
        shape.set_code_path(elm.attrib.get("code_path"))
        shape.set_params(elm.attrib.get("params", ""))
        shape.set_progress (float(elm.attrib.get("progress")))
        return shape

    def set_code_path(self, filepath, init=False):
        self.code_path = filepath
        filepath = Settings.Directory.get_full_path(filepath)
        if not os.path.isfile(filepath):
            return
        self.drawer_module = imp.load_source("drawer_module", filepath)
        if hasattr(self.drawer_module, "Drawer"):
            if self.drawer:
                old_params = copy_value(self.drawer.params)
            else:
                old_params = None
            self.drawer = self.drawer_module.Drawer()
            if hasattr(self.drawer, "params_info"):
                self.custom_props.clear()
                if old_params:
                    params = old_params
                else:
                    self.set_params(self.params)
                    params = self.drawer.params
                for name, data in self.drawer.params_info.items():
                    extras = None
                    for dk in data.keys():
                        if dk not in ("type", "default"):
                            if extras is None:
                                extras = dict()
                            extras[dk] = data[dk]
                    self.custom_props.add_prop(name, data["type"], extras)
                    if name not in params:
                        params[name] = data["default"]
                self.drawer.set_params(params)
            self.set_progress(self.progress)

    def has_prop(self, prop_name):
        if prop_name == "params" and len(self.custom_props.props)>0:
            return False
        if self.drawer and prop_name in self.drawer.params:
            return True
        return super(CustomShape, self).has_prop(prop_name)

    def get_prop_value(self, prop_name):
        if self.drawer and prop_name in self.drawer.params:
            return self.drawer.params[prop_name]
        return super(CustomShape, self).get_prop_value(prop_name)

    def set_prop_value(self, prop_name, value, prop_data=None):
        if self.drawer and prop_name in self.drawer.params:
            if self.drawer.params_info[prop_name]["type"] == "int":
                value = int(value)
            self.drawer.params[prop_name] = value
            self.drawer.set_params(self.drawer.params)#fake update
        return super(CustomShape, self).set_prop_value(prop_name, value, prop_data)

    def set_params(self, params):
        self.params = params
        if self.drawer and params:
            try:
                params_obj = eval(parser.expr("dict({0})".format(params)).compile())
                self.drawer.set_params(params_obj)
            except NameError:
                params_obj = dict()

    def set_progress(self, value):
        self.progress = value
        if self.drawer:
            self.drawer.set_progress(self.progress)

    def draw(self, ctx, drawing_size=None, fixed_border=True, root_shape=None, pre_matrix=None):
        self.fill_shape_area(ctx, root_shape=root_shape)

        ctx.save()
        if self.drawer:
            if hasattr(self.drawer, "use_custom_surface"):
                use_custom_surface = self.drawer.use_custom_surface
            else:
                use_custom_surface = True

            if use_custom_surface:
                custom_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(drawing_size.x), int(drawing_size.y))
                custom_ctx = cairo.Context(custom_surface)
                if pre_matrix:
                    custom_ctx.set_matrix(pre_matrix)
            else:
                custom_ctx = ctx

            self.pre_draw(custom_ctx, root_shape=root_shape)
            try:
                self.drawer.draw(custom_ctx, self.anchor_at.copy(), self.width, self.height, self)
            except BaseException as error:
                print('An exception occurred: {}'.format(error))
            custom_ctx = None
            if use_custom_surface:
                orig_mat = ctx.get_matrix()
                ctx.set_matrix(cairo.Matrix())
                ctx.set_source_surface(custom_surface)
                ctx.set_matrix(orig_mat)

                ctx.save()
                self.pre_draw(ctx, root_shape=root_shape)
                draw_rounded_rectangle(ctx, 0, 0, self.width, self.height, self.corner_radius)
                ctx.clip()
                ctx.paint()
                ctx.restore()
        ctx.restore()
        self.stroke_shape_area(ctx, fixed_border=fixed_border, root_shape=root_shape)
