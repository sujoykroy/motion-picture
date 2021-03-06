import math, numpy
from .point3d import Point3d
from .texture_map_color import *

DEG2PI = math.pi/180.

class Object3d(object):
    IdSeed = 0

    def __init__(self):
        self.rotation = Point3d(0, 0, 0)
        self.translation = Point3d(0, 0, 0)
        self.scale = Point3d(1, 1, 1)
        self.parent = None
        self.id_num = Object3d.IdSeed
        self.extra_reverse_matrix = None
        self.texture_resources = None

        self.border_color = None
        self.fill_color = None
        self.border_width = None

        Object3d.IdSeed += 1

    def __hash__(self):
        return hash(f'Object3d-{self.id_num}')

    def copy_into(self, other):
        other.rotation.copy_from(self.rotation)
        other.translation.copy_from(self.translation)
        other.scale.copy_from(self.scale)
        #other.border_color = copy_value(self.border_color)
        #other.fill_color = copy_value(self.fill_color)
        #other.border_width = self.border_width
        if self.extra_reverse_matrix is not None:
            other.extra_reverse_matrix = self.extra_reverse_matrix.copy()
        if self.texture_resources:
            other.texture_resources = self.texture_resources.copy()

    def get_active_fill_color(self):
        if self.fill_color is None and self.parent:
            return self.parent.get_active_fill_color()
        return self.fill_color

    def get_active_border_color(self):
        if self.border_color is None and self.parent:
            return self.parent.get_active_border_color()
        return self.border_color

    def get_active_border_width(self):
        if self.border_width is None and self.parent:
            return self.parent.get_active_border_width()
        return self.border_width

    def set_fill_color(self, color):
        self.fill_color = copy_value(color)

    def set_border_color(self, color):
        self.border_color = copy_value(color)

    def set_border_width(self, value):
        self.border_width = copy_value(value)

    def load_xml_elements(self, elm, exclude_border_fill=False):
        if self.rotation.get_x() !=0 or self.rotation.get_y() !=0 or self.rotation.get_z() !=0:
            elm.attrib["rot"] = self.rotation.to_text()
        if self.translation.get_x() !=0 or self.translation.get_y() !=0 or self.translation.get_z() !=0:
            elm.attrib["tr"] = self.translation.to_text()
        if self.scale.get_x() !=1 or self.scale.get_y() !=1 or self.scale.get_z()!=1:
            elm.attrib["sc"] = self.scale.to_text()
        if self.extra_reverse_matrix is not None and \
           not numpy.array_equal(self.extra_reverse_matrix, numpy.identity(4)):
            arr = []
            for i in range(self.extra_reverse_matrix.shape[0]):
                for j in range(self.extra_reverse_matrix.shape[1]):
                    arr.append("{0}".format(self.extra_reverse_matrix[i][j]))
            elm.attrib["mtx"] = ",".join(arr)
        if self.texture_resources is not None:
            elm.extend(self.texture_resources.get_xml_elements())
        if not exclude_border_fill:
            if self.fill_color is not None:
                elm.attrib["fc"] = Text.to_text(self.fill_color)
            if self.border_color is not None:
                elm.attrib["bc"] = Text.to_text(self.border_color)
            if self.border_width is not None:
                elm.attrib["bw"] = "{0}".format(self.border_width)


    def load_from_xml_elements(self, elm):
        rotation_text = elm.attrib.get("rot", None)
        if rotation_text:
            self.rotation.load_from_text(rotation_text)
        translation_text = elm.attrib.get("tr", None)
        if translation_text:
            self.translation.load_from_text(translation_text)
        scale_text = elm.attrib.get("sc", None)
        if scale_text:
            self.scale.load_from_text(scale_text)
        extra_reverse_matrix_text = elm.attrib.get("mtx", None)
        if extra_reverse_matrix_text:
            numbers = [float(v) for v in extra_reverse_matrix_text.split(",")]
            self.extra_reverse_matrix = numpy.array(numbers).reshape((4,4));

        for texture_elm in elm.findall(TextureResources.TAG_NAME):
            if self.texture_resources is None:
                self.texture_resources = TextureResources()
            self.texture_resources.add_resource_from_xml_element(texture_elm)

    def get_texture_resources(self):
        if self.texture_resources is None:
            if self.parent is not None:
                return self.parent.get_texture_resources()
        return self.texture_resources

    def __eq__(self, other):
        return isinstance(other, Object3d) and self.id_num == other.id_num

    def translate(self, point3d):
        point3d = Point3d.create_if_needed(point3d)
        self.translation.translate(point3d.values)

    def rotate_deg(self, point3d):
        point3d = Point3d.create_if_needed(point3d)
        self.rotation.translate(point3d.values*DEG2PI)

    def precalculate(self):
        self.build_matrices()

    def forward_transform_point_values(self, point_values, deep=True):
        if deep:
            parent = self.parent
            while parent:
                point_values = parent.forward_transform_point_values(point_values)
                parent = parent.parent
        point_values = numpy.matmul(self.forward_matrix, point_values.T).T
        point_values[:, 3] =1
        return point_values

    def reverse_transform_point_values(self, point_values, deep=True):
        point_values = numpy.matmul(self.reverse_matrix, point_values.T).T
        point_values[:, 3] =1
        if deep:
            if self.parent:
                point_values = self.parent.reverse_transform_point_values(point_values)
        return point_values

    def build_matrices(self):
        frotx = numpy.array([
            [1, 0                               , 0                              , 0],
            [0, math.cos(self.rotation.get_x()) , math.sin(self.rotation.get_x()), 0],
            [0, -math.sin(self.rotation.get_x()), math.cos(self.rotation.get_x()), 0],
            [0, 0                               , 0                             ,  1]
        ], dtype=numpy.float64)
        froty = numpy.array([
            [math.cos(self.rotation.get_y()), 0,  -math.sin(self.rotation.get_y()), 0],
            [0                              , 1,  0                               , 0],
            [math.sin(self.rotation.get_y()), 0,  math.cos(self.rotation.get_y()) , 0],
            [0                              , 0,  0                               , 1]
        ], dtype=numpy.float64)
        frotz = numpy.array([
            [math.cos(self.rotation.get_z()) , math.sin(self.rotation.get_z()),  0, 0],
            [-math.sin(self.rotation.get_z()), math.cos(self.rotation.get_z()),  0, 0],
            [0                               , 0                              ,  1, 0],
            [0                               , 0                              ,  0, 1]
        ], dtype=numpy.float64)

        rrotx = numpy.array([
            [1, 0                               , 0                               , 0],
            [0, math.cos(self.rotation.get_x()) , -math.sin(self.rotation.get_x()), 0],
            [0, math.sin(self.rotation.get_x()), math.cos(self.rotation.get_x())  , 0],
            [0, 0                               , 0                               , 1]
        ], dtype=numpy.float64)
        rroty = numpy.array([
            [math.cos(self.rotation.get_y()) , 0,  math.sin(self.rotation.get_y()) , 0],
            [0                               , 1,  0                               , 0],
            [-math.sin(self.rotation.get_y()), 0,  math.cos(self.rotation.get_y()) , 0],
            [0                               , 0,  0                               , 1]
        ], dtype=numpy.float64)
        rrotz = numpy.array([
            [math.cos(self.rotation.get_z()) , -math.sin(self.rotation.get_z()),  0, 0],
            [math.sin(self.rotation.get_z()) , math.cos(self.rotation.get_z()) ,  0, 0],
            [0                               , 0                               ,  1, 0],
            [0                               , 0                               ,  0, 1]
        ], dtype=numpy.float64)

        self.forward_matrix = numpy.identity(4, dtype=numpy.float64)
        self.forward_matrix = numpy.matmul(self.forward_matrix,
                    numpy.matmul(numpy.matmul(frotx, froty), frotz))
        self.forward_matrix = numpy.matmul(self.forward_matrix, numpy.diag(1./self.scale.values))
        self.forward_matrix = numpy.matmul(self.forward_matrix,
            numpy.array([
                [1,0,0,0],
                [0,1,0,0],
                [0,0,1,0],
                -self.translation.values
            ], dtype=numpy.float64).T
        )

        self.reverse_matrix = numpy.matmul(numpy.matmul(rrotx, rroty), rrotz)
        self.reverse_matrix = numpy.matmul(self.reverse_matrix, numpy.diag(self.scale.values))
        self.reverse_matrix = numpy.matmul(self.reverse_matrix,
            numpy.array([
                [1,0,0,0],
                [0,1,0,0],
                [0,0,1,0],
                self.translation.values
            ], dtype=numpy.float64).T
        )
        if self.extra_reverse_matrix is not None:
            self.reverse_matrix = numpy.matmul(self.reverse_matrix, self.extra_reverse_matrix)
            self.forward_matrix = numpy.matmul(self.reverse_matrix,
                    numpy.linalg.inv(self.extra_reverse_matrix))

