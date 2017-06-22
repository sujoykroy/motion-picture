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
        self.doc_box = RectangleShape(
                anchor_at=Point(0, 0),
                border_color = None, border_width = 0, fill_color= None,
                width = 1, height = 1, corner_radius=0)
        self.doc_box.parent_shape = self

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
            self.doc_main_multi_shape.parent_shape = self.doc_box
            self.doc_width = wh[0]
            self.doc_height = wh[1]

            timelines = self.doc_main_multi_shape.timelines
            if self.time_line_name not in timelines and len(timelines)>0:
                self.set_time_line_name(timelines.keys()[0])

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
            self.doc_box.width = self.doc_width
            self.doc_box.height = self.doc_height

            sx = float(self.width)/self.doc_width
            sy = float(self.height)/self.doc_height
            self.doc_box.scale_x = sx
            self.doc_box.scale_y = sy

            self.doc_box.anchor_at.assign(self.doc_width*.5, self.doc_height*.5)
            self.doc_box.move_to(self.width*.5, self.height*.5)

            camera = self.camera_obj
            if not camera:
                camera = self.doc_main_multi_shape.camera
            #camera = None
            if camera:
                width = camera.width
                height = camera.height
            else:
                width = self.width
                height = self.height

            sx = float(width)/self.doc_width
            sy = float(height)/self.doc_height

            doc_ctx = cairo.Context(doc_surface)
            if pre_matrix:
                doc_ctx.set_matrix(pre_matrix)

            #doc_ctx.scale(sx ,sy)
            if camera:
                camera.reverse_pre_draw(doc_ctx, root_shape=self.doc_box)
            self.doc_main_multi_shape.draw(doc_ctx,
                drawing_size = drawing_size, fixed_border=fixed_border,
                pre_matrix=pre_matrix
            )
            orig_mat = ctx.get_matrix()
            if pre_matrix:
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
