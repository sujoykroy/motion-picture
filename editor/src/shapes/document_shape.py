from rectangle_shape import RectangleShape
from ..commons import *

class DocumentShape(RectangleShape):
    TYPE_NAME = "document"

    Loader = None

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius):
        super(DocumentShape, self).__init__(
                anchor_at, border_color, border_width,
                                fill_color, width, height, corner_radius)
        self.document_path = None
        self.time_line_name = None
        self.camera = None
        self.doc_main_multi_shape = None
        self.time_line_obj = None
        self.camera_obj = None
        self.doc_width = 1
        self.doc_height = 1
        self.time_pos = 0

    def copy(self, copy_name=False, deep_copy=False):
        newob = DocumentShape(self.anchor_at.copy(), copy_value(self.border_color), self.border_width,
                              copy_value(self.fill_color), self.width, self.height, self.corner_radius)
        self.copy_into(newob, copy_name)
        newob.set_document_path(self.document_path)
        newob.set_time_line_name(self.time_line_name)
        newob.set_camera(self.camera)
        return newob

    def get_xml_element(self):
        elm = RectangleShape.get_xml_element(self)
        elm.attrib["document_path"] = self.document_path
        if self.time_line_name:
            elm.attrib["time_line"] = self.time_line_name
        if self.camera:
            elm.attrib["camera"] = self.camera
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        shape = super(DocumentShape, cls).create_from_xml_element(elm)
        shape.set_document_path(elm.attrib.get("document_path"))
        shape.set_time_line_name(elm.attrib.get("time_line"))
        shape.set_camera(elm.attrib.get("camera"))
        return shape

    def load_document(self):
        if not self.document_path or self.document_path == "//":
            self.doc_main_multi_shape = None
            return
        if self.document_path and not self.doc_main_multi_shape:
            wh, self.doc_main_multi_shape = \
                    DocumentShape.Loader.load_and_get_main_multi_shape(self.document_path)
            self.doc_main_multi_shape = self.doc_main_multi_shape.copy(
                            deep_copy=True, copy_name=True)
            self.doc_width = wh[0]
            self.doc_height = wh[1]

            self.time_line_obj = None
            self.time_line_name = None
            self.camera = None
            self.camera_obj = None
            timelines = self.doc_main_multi_shape.timelines
            if self.time_line_name not in timelines and len(timelines)>0:
                self.set_time_line_name(timelines.keys()[0])

    @classmethod
    def get_time_line_for(self, document_path, time_line_name):
        wh, doc_main_multi_shape = \
                    DocumentShape.Loader.load_and_get_main_multi_shape(document_path)
        return doc_main_multi_shape.timelines.get(time_line_name)

    def unload_document(self):
        if self.doc_main_multi_shape:
            self.doc_main_multi_shape.cleanup()
            self.doc_main_multi_shape = None

    def set_document_path(self, path):
        if self.document_path != path or self.doc_main_multi_shape is None:
            self.document_path = path
            self.unload_document()
            self.load_document()

    def set_time_line_name(self, time_line):
        if self.time_line_name != time_line:
            self.time_line_name = time_line
            self.load_document()
            if self.doc_main_multi_shape:
                self.time_line_obj = self.doc_main_multi_shape.timelines.get(self.time_line_name)

    def set_camera(self, camera):
        if self.camera != camera:
            self.camera = camera
            self.load_document()
            self.camera_obj = self.doc_main_multi_shape.shapes.get_item_by_name(self.camera)

    def set_time_pos(self, value, prop_data=None):
        if prop_data:
            self.set_document_path(prop_data.get("document_path"))
            self.set_time_line_name(prop_data.get("time_line_name"))
            self.set_camera(prop_data.get("camera"))
        self.time_pos = value
        if self.time_line_obj:
            self.time_line_obj.move_to(self.time_pos)

    def get_duration(self):
        if self.time_line_obj:
            return self.time_line_obj.duration
        else:
            return 10

    def get_time_line_length(self):
        return "{0:.2f} sec".format(self.get_duration())

    def set_prop_value(self, prop_name, prop_value, prop_data=None):
        if prop_name == "time_pos":
            self.set_time_pos(prop_value, prop_data)
        else:
            super(DocumentShape, self).set_prop_value(prop_name, prop_value, prop_data)

    def draw_path(self, ctx, for_fill=False):
        draw_rounded_rectangle(ctx, 0, 0, self.width, self.height, self.corner_radius)

    def draw(self, ctx, drawing_size=None,
                        fixed_border=True, no_camera=True,
                        root_shape=None, exclude_camera_list=None,
                        pre_matrix=None, show_non_renderable=False):
        if self.fill_color is not None:
            ctx.save()
            self.pre_draw(ctx, root_shape=root_shape)
            self.draw_path(ctx, for_fill=True)
            self.draw_fill(ctx)
            ctx.restore()

        if self.doc_main_multi_shape:
            doc_surface = cairo.ImageSurface(
                        cairo.FORMAT_ARGB32, int(drawing_size.x), int(drawing_size.y))

            camera = self.camera_obj
            if not camera:
                camera = self.doc_main_multi_shape.camera

            if camera:
                sx = float(self.width)/float(camera.width)
                sy = float(self.height)/float(camera.height)
            else:
                sx = float(self.width)/self.doc_width
                sy = float(self.height)/self.doc_height

            doc_ctx = cairo.Context(doc_surface)
            set_default_line_style(doc_ctx)
            if pre_matrix:
                doc_ctx.set_matrix(pre_matrix)
            #doc_ctx = ctx
            #doc_ctx.save()
            self.pre_draw(doc_ctx, root_shape=root_shape)
            doc_ctx.scale(sx ,sy)

            if camera:
                camera.reverse_pre_draw(doc_ctx, root_shape=root_shape)

            #doc_ctx.save()
            self.doc_main_multi_shape.draw(doc_ctx,
                drawing_size = drawing_size, fixed_border=fixed_border,
                pre_matrix=doc_ctx.get_matrix()
            )
            #doc_ctx.restore()
            """
            if camera:
                doc_ctx.save()
                camera.pre_draw(doc_ctx, root_shape=root_shape)
                camera.draw_path(doc_ctx)
                #camera.draw_anchor(doc_ctx)
                draw_stroke(doc_ctx, 2, "00ff00")
                doc_ctx.restore()
            doc_ctx.restore()
            """

            orig_mat = ctx.get_matrix()
            ctx.set_matrix(cairo.Matrix())
            ctx.set_source_surface(doc_surface)
            ctx.set_matrix(orig_mat)

            ctx.save()
            self.pre_draw(ctx, root_shape=root_shape)
            self.draw_path(ctx)
            ctx.clip()
            ctx.paint()
            ctx.restore()

        if self.border_color is not None:
            ctx.save()
            self.pre_draw(ctx, root_shape=root_shape)
            self.draw_path(ctx, for_fill=False)
            if fixed_border:
                ctx.restore()
                self.draw_border(ctx)
            else:
                self.draw_border(ctx)
                ctx.restore()



    def cleanup(self):
        if self.doc_main_multi_shape:
            self.doc_main_multi_shape.cleanup()
        super(DocumentShape, self).cleanup()
