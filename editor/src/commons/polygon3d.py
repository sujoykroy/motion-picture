import numpy

from object3d import Object3d
from texture_map_color import TextureMapColor
from misc import *
from draw_utils import *

from xml.etree.ElementTree import Element as XmlElement

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
        if self.fill_color:
            elm.attrib["fc"] = self.fill_color.to_text()
        if self.border_color:
            elm.attrib["bc"] = self.border_color.to_text()
        if self.border_width:
            elm.attrib["bw"] = "{0}".format(self.border_width)
        elm.text = ",".join(self.point_indices);
        return elm

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
        while fill_color is None and parent is not None:
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

    @classmethod
    def create_if_needed(cls, parent, data):
        if data is None or isinstance(data, Polygon3d):
            return data
        return Polygon3d(parent=parent, point_indices=data)
