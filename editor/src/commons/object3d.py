import math, numpy
from point3d import Point3d

DEG2PI = math.pi/180.

class Object3d(object):
    IdSeed = 0

    def __init__(self):
        self.rotation = Point3d(0, 0, 0)
        self.translation = Point3d(0, 0, 0)
        self.scale = Point3d(1, 1, 1)
        self.rotation_matrix  = None
        self.parent = None
        self.id_num = Object3d.IdSeed
        self.extra_reverse_matrix = None
        self.texture_resources = None
        Object3d.IdSeed += 1

    def load_xml_elements(self, elm):
        if self.rotation.get_x() !=0 or self.rotation.get_y() !=0 or self.rotation.get_z() !=0:
            elm.attrib["rot"] = self.rotation.to_text()
        if self.translation.get_x() !=0 or self.translation.get_y() !=0 or self.translation.get_z() !=0:
            elm.attrib["tr"] = self.translation.to_text()
        if self.scale.get_x() !=1 or self.scale.get_y() !=1 or self.scale.get_z()!=1:
            elm.attrib["sc"] = self.scale.to_text()
        if self.extra_reverse_matrix is not None:
            arr = []
            for i in range(self.extra_reverse_matrix.shape[0]):
                for j in range(self.extra_reverse_matrix.shape[1]):
                    arr.append("{0}".format(self.extra_reverse_matrix[i][j]))
            elm.attrib["mtx"] = ",".join(arr)

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
        self.build_rotation_matrix()

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

    def build_rotation_matrix(self):
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

