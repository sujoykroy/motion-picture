import numpy

from object3d import Object3d
from texture_map_color import TextureMapColor
from misc import *
from draw_utils import *
from colors import Color

from xml.etree.ElementTree import Element as XmlElement

#from OpenGL.EGL import *
from ctypes import *
from OpenGL.GL import *

FLOAT_BYTE_COUNT = 4;
SHORT_BYTE_COUNT = 2;
COORDS_PER_VERTEX = 3;
VERTEX_STRIDE = COORDS_PER_VERTEX*FLOAT_BYTE_COUNT;
COORDS_PER_TEXTURE = 2;
TEXTURE_STRIDE = COORDS_PER_TEXTURE*FLOAT_BYTE_COUNT;

class Polygon3d(Object3d):
    TAG_NAME = "pl3"
    Items = []

    def __init__(self, parent, point_indices, temporary=False,
                       closed=True, kind="linear",
                       border_color="000000", fill_color="CCCCCC", border_width=1):
        super(Polygon3d, self).__init__()

        self.border_color = copy_value(border_color)
        self.fill_color = copy_value(fill_color)
        self.border_width = border_width

        self.parent = parent
        self.kind = kind
        self.point_indices = list(point_indices)

        self.closed = closed
        self.z_depths = dict()

        self.plane_params = dict()
        self.bounding_rect = dict()
        self.plane_params_normalized = dict()
        if not temporary:
            Polygon3d.Items.append(self)

        self.gl_vertices = None
        self.is_line_drawing = False
    """
    def copy(self):
        newob = Polygon3d(
            parent=self.parent,
            point_indices=self.point_indices[: -1 if self.closed else None],
            closed=self.closed,
            border_color=self.border_color,
            fill_color=self.fill_color,
            border_width=self.border_width)
        return newob
    """

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        self.load_xml_elements(elm)
        if not self.closed:
            elm.attrib["closed"] = "0";
        point_indices_elm = XmlElement("pi")
        point_indices_elm.text = ",".join(str(p) for p in self.point_indices)
        elm.append(point_indices_elm)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        border_color = color_from_text(elm.attrib.get("bc", None))
        fill_color = color_from_text(elm.attrib.get("fc", None))
        border_width = elm.attrib.get("border_width", None)
        if border_width is not None:
            border_width = float(border_width)
        point_indices = [int(p) for p in elm.find("pi").text.split(",")]
        newob = cls(parent=None, point_indices=point_indices,
                    border_color=border_color, fill_color=fill_color,
                    border_width=border_width)
        newob.load_from_xml_elements(elm)
        return newob

    def get_z_cut(self, camera, x, y):
        plane_params =self.plane_params[camera]
        if plane_params is None:
            return 10000
        if plane_params[2] == 0:
            return 10000
        return (-plane_params[3]-plane_params[0]*x-plane_params[1]*y)/plane_params[2]

    def build_projection(self, camera):
        world_point_values = self.parent.world_point_values[self.point_indices]
        camera_point_values = camera.forward_transform_point_values(world_point_values)[:, :3]
        self.z_depths[camera] = numpy.amax(camera_point_values[:,2])
        if camera_point_values.shape[0]>2:
            ab = camera_point_values[1, :]-camera_point_values[0, :]
            bc = camera_point_values[2, :]-camera_point_values[0, :]
            abc = numpy.cross(ab, bc)
            d = -numpy.dot(abc,camera_point_values[0, :])
            self.plane_params[camera] = numpy.append(abc, d)
            self.plane_params_normalized[camera] = numpy.array([
                -abc[0]/abc[2], -abc[1]/abc[2], -d/abc[2]
            ])
        else:
            self.plane_params[camera] = None
            self.plane_params_normalized[camera] = numpy.array([
                0, 0, 0
            ])

        camera_point_values = camera.viewer_point_values(camera_point_values)
        self.bounding_rect[camera] = [
            numpy.min(camera_point_values, axis=0),
            numpy.max(camera_point_values, axis=0),
        ]

    def get_points(self):
        return self.parent.world_point_values[self.point_indices]

    def get_camera_points(self, camera):
        world_point_values = self.parent.world_point_values[self.point_indices]
        return camera.forward_transform_point_values(world_point_values)

    def draw_path(self, ctx, camera):
        projected_values = self.parent.point_projections[camera][self.point_indices, :]
        ctx.new_path()
        for i in range(projected_values.shape[0]):
            values = projected_values[i]
            if i == 0:
                ctx.move_to(values[0], values[1])
            else:
                ctx.line_to(values[0], values[1])
        if self.closed:
            ctx.line_to(projected_values[0][0], projected_values[0][1])


    def draw(self, ctx, camera, border_color=-1, border_width=-1):
        if border_color == -1:
            border_color = self.border_color
            parent = self.parent
            while border_color is None and parent is not None:
                border_color = parent.border_color
                parent = parent.parent

        if border_width == -1:
            border_width = self.border_width
            parent = self.parent
            while border_width is None and parent is not None:
                border_width = parent.border_width
                parent = parent.parent

        fill_color = self.fill_color
        parent = self.parent
        while fill_color is None and parent is not None and hasattr(parent, "fill_color"):
            fill_color = parent.fill_color
            parent = parent.parent

        if fill_color is not None:
            if isinstance(fill_color, TextureMapColor):
                #border_color = "000000"
                fill_color.build()
                projected_values = self.parent.point_projections[camera][self.point_indices, :]
                orig_projected_values=projected_values
                orig_texcoords = fill_color.texcoords[0]
                if orig_projected_values.shape[0] == 3:
                    point_count = orig_projected_values.shape[0]-2
                else:
                    point_count = orig_projected_values.shape[0]-2
                for oi in range(0,  orig_projected_values.shape[0]-1, 2):
                    projected_values=orig_projected_values[oi:oi+3, :]
                    texcoords = orig_texcoords[oi:oi+3, :]
                    if oi+2 == orig_projected_values.shape[0]:
                        projected_values = numpy.concatenate(
                            (projected_values, [orig_projected_values[0, :]]), axis=0)
                        texcoords = numpy.concatenate(
                            (texcoords, [orig_texcoords[0, :]]), axis=0)
                    avg_projected_values = numpy.average(projected_values, axis=0)
                    projected_values = numpy.concatenate((
                        projected_values, numpy.array([numpy.ones(projected_values.shape[0], dtype="f")]).T
                    ), axis=1)
                    nmtrx = numpy.matmul(projected_values.T, numpy.linalg.inv(texcoords.T))
                    mtrx = cairo.Matrix(xx=float(nmtrx[0][0]), xy=float(nmtrx[0][1]), x0=float(nmtrx[0][2]),
                                yx=float(nmtrx[1][0]), yy=float(nmtrx[1][1]), y0=float(nmtrx[1][2]))
                    for antalias in [True]:
                        ctx.save()
                        ctx.set_antialias(antalias)
                        ctx.set_matrix(mtrx.multiply(ctx.get_matrix()))
                        ctx.set_source_surface(fill_color.get_surface())
                        ctx.get_source().set_filter(cairo.FILTER_FAST)

                        ctx.new_path()
                        for i in range(texcoords.shape[0]):
                            values = texcoords[i]
                            if i == 0:
                                ctx.move_to(values[0], values[1])
                            else:
                                ctx.line_to(values[0], values[1])
                        ctx.line_to(texcoords[0][0], texcoords[0][1])
                        ctx.clip()
                        ctx.paint()
                        ctx.set_antialias(False)
                        #avg_tex_values = numpy.average(texcoords, axis=0)
                        #draw_text(ctx, text_color="FF00FF", font_name="50",
                        #    x=avg_tex_values[0],
                        #    y=avg_tex_values[1],
                        #    text="{0}".format(self.id_num),
                        #)
                        ctx.restore()
                        #draw_stroke(ctx, border_width, border_color)
                        #border_color = None
            else:
                ctx.save()
                self.draw_path(ctx, camera)
                ctx.restore()
                draw_fill(ctx, fill_color)

        if border_color is not None and border_width is not None:
            ctx.save()
            ctx.set_antialias(True)
            self.draw_path(ctx, camera)
            ctx.restore()
            mat = ctx.get_matrix()
            ctx.set_matrix(cairo.Matrix())
            draw_stroke(ctx, border_width, border_color)
            ctx.set_matrix(mat)

        if False:
            for point_index in self.point_indices:
                proj_value = self.parent.point_projections[camera][point_index, :]
                ctx.save()
                ctx.arc(proj_value[0], proj_value[1], 2, 0, 2*math.pi)
                ctx.restore()
                draw_stroke(ctx, 1, "FF4400")

    def build_gl_buffers(self):
        vertices = numpy.array([]).astype("f")

        for i in range(len(self.point_indices)):
            point3d = self.parent.points[self.point_indices[i]]
            vertices = numpy.append(vertices, point3d.values[:3])
        vertices.shape = (len(self.point_indices), 3)

        if isinstance(self.fill_color, TextureMapColor):
            texcoords = self.fill_color.texcoords[0][:, :2]
            texcoords = (-1, 2)
            vertices = numpy.concatenate((vertices, texcoords), axis=1).astype("f")
            stride_count = 5
        else:
            stride_count = 3
        vertices.shape = (-1,)
        self.gl_vertices = vertices = numpy.ascontiguousarray(vertices)
        self.gl_vertices_stride = vertices.dtype.itemsize*stride_count
        if len(self.point_indices)<=3:
            vertex_order_count = len(self.point_indices)
        else:
            vertex_order_count = 3+(len(self.point_indices)-3)*3
        vertex_order_data = numpy.array([]).astype(numpy.uint16)
        start_counter = 0
        for i in range(0, vertex_order_count, 3):
            vertex_order_data = numpy.append(vertex_order_data, [0, start_counter+1, start_counter+2])
            start_counter += 1
        self.gl_vertex_order_data = numpy.ascontiguousarray(vertex_order_data)
        self.gl_vertex_line_order_data = numpy.ascontiguousarray(numpy.array(
                list(range(len(self.point_indices)))).astype(numpy.uint16))

    def draw_gl(self, pre_matrix, threed_gl_render_context):
        drawer = threed_gl_render_context.get_drawer()
        glUseProgram(drawer.gl_program)
        if self.gl_vertices is None:
            self.build_gl_buffers()

        drawer.mvp_matrix_handle = glGetUniformLocation(drawer.gl_program, 'uMVPMatrix')
        glUniformMatrix4fv(drawer.mvp_matrix_handle, 1, GL_FALSE, pre_matrix, 0)

        glBindBuffer(GL_ARRAY_BUFFER, drawer.vbo)
        glBufferData(GL_ARRAY_BUFFER,
            self.gl_vertices.dtype.itemsize*self.gl_vertices.size, self.gl_vertices, GL_STATIC_DRAW)

        drawer.gl_position_handle = glGetAttribLocation(drawer.gl_program, 'aPosition')
        glEnableVertexAttribArray(drawer.gl_position_handle)
        glVertexAttribPointer(drawer.gl_position_handle,
                COORDS_PER_VERTEX, GL_FLOAT, GL_FALSE, self.gl_vertices_stride, ctypes.c_void_p(0))

        drawer.gl_has_texture_handle = glGetUniformLocation(drawer.gl_program, 'uHasTexture')
        if isinstance(self.fill_color, TextureMapColor) and not self.is_line_drawing:
            glUniform1i(drawer.gl_has_texture_handle, 1)

            drawer.gl_tex_coords_handle = glGetAttribLocation(drawer.gl_program, 'aTexCoords')
            glEnableVertexAttribArray(drawer.gl_tex_coords_handle)
            glVertexAttribPointer(drawer.gl_tex_coords_handle,
                    COORDS_PER_TEXTURE, GL_FLOAT, GL_FALSE, self.gl_vertices_stride,
                    c_void_p(COORDS_PER_VERTEX*self.gl_vertices.dtype.itemsize))

            drawer.gl_texture_handle = glGetUniformLocation(drawer.gl_program, 'uTexture')
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D,
                    threed_gl_render_context.get_texture_handle(
                           self.fill_color.get_resource_name()))
            glUniform1i(drawer.gl_texture_handle, 0)
        else:
            glUniform1i(drawer.gl_has_texture_handle, 0)
            fill_color = self.get_active_fill_color()
            if isinstance(fill_color, Color):
                drawer.gl_color_handle = glGetUniformLocation(drawer.gl_program, 'uColor')
                glUniform4fv(drawer.gl_color_handle, 1,
                        fill_color.get_gl_array_value(), 0)
        if not self.is_line_drawing:
            glDrawElements(GL_TRIANGLES, len(self.gl_vertex_order_data),
                    GL_UNSIGNED_SHORT, self.gl_vertex_order_data)
        else:
            glDrawElements(GL_LINES, len(self.gl_vertex_line_order_data),
                    GL_UNSIGNED_SHORT, self.gl_vertex_line_order_data)

        border_color = self.get_active_border_color()
        if border_color is not None and self.get_active_border_width() is not None:
            if isinstance(border_color, Color):
                drawer.gl_color_handle = glGetUniformLocation(drawer.gl_program, 'uColor')
                glUniform4fv(drawer.gl_color_handle, 1,
                        border_color.get_gl_array_value(), 0)
            glUniform1i(drawer.gl_has_texture_handle, 0)
            glLineWidth(self.get_active_border_width())
            glDrawElements(GL_LINES, len(self.gl_vertex_line_order_data),
                    GL_UNSIGNED_SHORT, self.gl_vertex_line_order_data)
        glDisableVertexAttribArray(drawer.gl_position_handle)

    @classmethod
    def create_if_needed(cls, parent, data):
        if data is None or isinstance(data, Polygon3d):
            return data
        return Polygon3d(parent=parent, point_indices=data)
